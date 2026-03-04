from __future__ import annotations

import secrets
import uuid
from datetime import date
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.request_context import get_request_id
from app.core.security import now_utc
from app.models.audit_event import AuditEvent
from app.models.customer import Customer
from app.models.enquiry import Enquiry, EnquiryItem, EnquiryStatusHistory
from app.models.product import Product
from app.models.user import User
from app.schemas.enquiries import EnquiryCreate, EnquiryStatus, EnquiryStatusTransitionRequest

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    EnquiryStatus.RECEIVED.value: {EnquiryStatus.IN_REVIEW.value, EnquiryStatus.CANCELLED.value},
    EnquiryStatus.IN_REVIEW.value: {EnquiryStatus.QUOTED.value, EnquiryStatus.CANCELLED.value},
    EnquiryStatus.QUOTED.value: {
        EnquiryStatus.PENDING_APPROVAL.value,
        EnquiryStatus.IN_REVIEW.value,
        EnquiryStatus.CANCELLED.value,
    },
    EnquiryStatus.PENDING_APPROVAL.value: {
        EnquiryStatus.APPROVED.value,
        EnquiryStatus.REJECTED.value,
        EnquiryStatus.CANCELLED.value,
    },
    EnquiryStatus.APPROVED.value: {EnquiryStatus.PO_CREATED.value, EnquiryStatus.CANCELLED.value},
    EnquiryStatus.REJECTED.value: {EnquiryStatus.IN_REVIEW.value, EnquiryStatus.CANCELLED.value},
    EnquiryStatus.PO_CREATED.value: {
        EnquiryStatus.INVOICED.value,
        EnquiryStatus.IN_DELIVERY.value,
        EnquiryStatus.CANCELLED.value,
    },
    EnquiryStatus.INVOICED.value: {
        EnquiryStatus.IN_DELIVERY.value,
        EnquiryStatus.CLOSED.value,
        EnquiryStatus.CANCELLED.value,
    },
    EnquiryStatus.IN_DELIVERY.value: {
        EnquiryStatus.DELIVERED.value,
        EnquiryStatus.CANCELLED.value,
    },
    EnquiryStatus.DELIVERED.value: {EnquiryStatus.CLOSED.value},
    EnquiryStatus.CLOSED.value: set(),
    EnquiryStatus.CANCELLED.value: set(),
}


def is_transition_allowed(current_status: str, next_status: str) -> bool:
    return next_status in ALLOWED_TRANSITIONS.get(current_status, set())


class EnquiryService:
    def __init__(self, db: Session):
        self.db = db

    def list_enquiries(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        status_filter: EnquiryStatus | None = None,
    ) -> list[Enquiry]:
        stmt = (
            select(Enquiry)
            .options(selectinload(Enquiry.items))
            .order_by(Enquiry.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        if status_filter is not None:
            stmt = stmt.where(Enquiry.status == status_filter.value)
        return list(self.db.scalars(stmt))

    def get_enquiry(self, enquiry_id: uuid.UUID) -> Enquiry:
        enquiry = self.db.scalar(
            select(Enquiry).options(selectinload(Enquiry.items)).where(Enquiry.id == enquiry_id)
        )
        if enquiry is None:
            raise self._not_found("enquiry")
        return enquiry

    def create_enquiry(self, payload: EnquiryCreate, actor_user: User) -> Enquiry:
        if self.db.get(Customer, payload.customer_id) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="customer_id does not exist",
            )

        product_ids = {item.product_id for item in payload.items}
        existing_product_ids = set(
            self.db.scalars(select(Product.id).where(Product.id.in_(product_ids)))
        )
        missing_products = sorted(str(item) for item in product_ids - existing_product_ids)
        if missing_products:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"unknown product_id values: {', '.join(missing_products)}",
            )

        enquiry = Enquiry(
            enquiry_no=self._generate_enquiry_no(),
            customer_id=payload.customer_id,
            owner_user_id=actor_user.id,
            status=EnquiryStatus.RECEIVED.value,
            received_date=payload.received_date or date.today(),
            currency=payload.currency.upper(),
            notes=payload.notes,
        )
        self.db.add(enquiry)
        self.db.flush()

        for item in payload.items:
            self.db.add(
                EnquiryItem(
                    enquiry_id=enquiry.id,
                    product_id=item.product_id,
                    requested_qty=item.requested_qty,
                    target_price=item.target_price,
                    notes=item.notes,
                )
            )

        self.db.add(
            EnquiryStatusHistory(
                enquiry_id=enquiry.id,
                from_status=None,
                to_status=EnquiryStatus.RECEIVED.value,
                changed_by=actor_user.id,
                comment="enquiry created",
            )
        )
        self.db.add(
            AuditEvent(
                actor_user_id=actor_user.id,
                entity_type="enquiry",
                entity_id=enquiry.id,
                action="CREATE",
                before_jsonb={},
                after_jsonb=self._status_snapshot(enquiry.status),
                request_id=get_request_id(),
            )
        )

        self._commit()
        return self.get_enquiry(enquiry.id)

    def transition_status(
        self,
        enquiry_id: uuid.UUID,
        payload: EnquiryStatusTransitionRequest,
        actor_user: User,
    ) -> Enquiry:
        enquiry = self.get_enquiry(enquiry_id)
        target_status = payload.to_status.value

        if enquiry.status == target_status:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"enquiry already in status {target_status}",
            )

        if not is_transition_allowed(enquiry.status, target_status):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"invalid transition: {enquiry.status} -> {target_status}",
            )

        previous_status = enquiry.status
        enquiry.status = target_status
        enquiry.updated_at = now_utc()

        self.db.add(
            EnquiryStatusHistory(
                enquiry_id=enquiry.id,
                from_status=previous_status,
                to_status=target_status,
                changed_by=actor_user.id,
                comment=payload.comment,
            )
        )
        self.db.add(
            AuditEvent(
                actor_user_id=actor_user.id,
                entity_type="enquiry",
                entity_id=enquiry.id,
                action="STATUS_CHANGE",
                before_jsonb=self._status_snapshot(previous_status),
                after_jsonb=self._status_snapshot(target_status),
                request_id=get_request_id(),
            )
        )

        self._commit()
        return self.get_enquiry(enquiry.id)

    def history(self, enquiry_id: uuid.UUID) -> list[EnquiryStatusHistory]:
        _ = self.get_enquiry(enquiry_id)
        return list(
            self.db.scalars(
                select(EnquiryStatusHistory)
                .where(EnquiryStatusHistory.enquiry_id == enquiry_id)
                .order_by(EnquiryStatusHistory.changed_at.asc())
            )
        )

    def _generate_enquiry_no(self) -> str:
        now = now_utc()
        suffix = secrets.token_hex(2).upper()
        return f"ENQ-{now:%Y%m%d-%H%M%S}-{suffix}"

    @staticmethod
    def _status_snapshot(status_value: str) -> dict[str, Any]:
        return {"status": status_value}

    @staticmethod
    def _not_found(entity: str) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity} not found",
        )

    def _commit(self) -> None:
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc.orig),
            ) from exc
