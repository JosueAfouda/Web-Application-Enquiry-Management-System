from __future__ import annotations

import secrets
import uuid
from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.request_context import get_request_id
from app.core.security import now_utc
from app.models.audit_event import AuditEvent
from app.models.enquiry import Enquiry, EnquiryItem
from app.models.product import Product
from app.models.quotation import Approval, Quotation, QuotationItem, QuotationRevision
from app.models.user import User
from app.schemas.quotations import QuotationCreateRequest, QuotationRevisionCreateRequest

DECIMAL_TWO = Decimal("0.01")


class QuotationService:
    def __init__(self, db: Session):
        self.db = db

    def create_quotation(
        self,
        enquiry_id: uuid.UUID,
        payload: QuotationCreateRequest,
        actor_user: User,
    ) -> Quotation:
        enquiry = self.db.get(Enquiry, enquiry_id)
        if enquiry is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="enquiry not found",
            )

        if payload.quotation_no:
            quotation_no = payload.quotation_no.strip()
        else:
            quotation_no = self._generate_quotation_no()
        quotation = Quotation(
            enquiry_id=enquiry.id,
            quotation_no=quotation_no,
            current_revision_no=0,
            status="DRAFT",
        )
        self.db.add(quotation)
        self.db.flush()

        self.db.add(
            AuditEvent(
                actor_user_id=actor_user.id,
                entity_type="quotation",
                entity_id=quotation.id,
                action="CREATE",
                before_jsonb={},
                after_jsonb={"status": quotation.status, "quotation_no": quotation.quotation_no},
                request_id=get_request_id(),
            )
        )

        self._commit()
        return self.get_quotation(quotation.id)

    def create_revision(
        self,
        quotation_id: uuid.UUID,
        payload: QuotationRevisionCreateRequest,
        actor_user: User,
    ) -> QuotationRevision:
        quotation = self._get_quotation_or_404(quotation_id)

        if self._has_pending_submitted_revision(quotation.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="cannot create revision while another submitted revision is pending",
            )

        self._validate_revision_items(quotation.enquiry_id, payload)
        next_revision_no = self._next_revision_no(quotation.id)

        subtotal = self._calculate_subtotal(payload)
        total = self._calculate_total(subtotal, payload.freight, payload.markup_percent)

        revision = QuotationRevision(
            quotation_id=quotation.id,
            revision_no=next_revision_no,
            freight=self._quantize(payload.freight),
            markup_percent=payload.markup_percent,
            subtotal=subtotal,
            total=total,
            currency=payload.currency.upper(),
            created_by=actor_user.id,
        )
        self.db.add(revision)
        self.db.flush()

        for item in payload.items:
            line_total = self._quantize(item.qty * item.unit_price)
            self.db.add(
                QuotationItem(
                    revision_id=revision.id,
                    enquiry_item_id=item.enquiry_item_id,
                    product_id=item.product_id,
                    qty=item.qty,
                    unit_price=item.unit_price,
                    line_total=line_total,
                    notes=item.notes,
                )
            )

        self.db.add(
            Approval(
                revision_id=revision.id,
                step_name="FINAL",
                decision="PENDING",
            )
        )

        quotation.current_revision_no = next_revision_no
        quotation.status = "DRAFT"
        quotation.updated_at = now_utc()

        self.db.add(
            AuditEvent(
                actor_user_id=actor_user.id,
                entity_type="quotation_revision",
                entity_id=revision.id,
                action="CREATE",
                before_jsonb={},
                after_jsonb={
                    "quotation_id": str(quotation.id),
                    "revision_no": revision.revision_no,
                    "subtotal": str(revision.subtotal),
                    "total": str(revision.total),
                },
                request_id=get_request_id(),
            )
        )

        self._commit()
        return self.get_revision(quotation.id, revision.id)

    def get_quotation(self, quotation_id: uuid.UUID) -> Quotation:
        quotation = self.db.scalar(
            select(Quotation)
            .options(
                selectinload(Quotation.revisions).selectinload(QuotationRevision.items),
                selectinload(Quotation.revisions).selectinload(QuotationRevision.approvals),
            )
            .where(Quotation.id == quotation_id)
        )
        if quotation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="quotation not found")
        quotation.revisions.sort(key=lambda r: r.revision_no)
        return quotation

    def get_revision(self, quotation_id: uuid.UUID, revision_id: uuid.UUID) -> QuotationRevision:
        revision = self.db.scalar(
            select(QuotationRevision)
            .options(
                selectinload(QuotationRevision.items),
                selectinload(QuotationRevision.approvals),
            )
            .where(
                QuotationRevision.id == revision_id,
                QuotationRevision.quotation_id == quotation_id,
            )
        )
        if revision is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="quotation revision not found",
            )
        return revision

    def submit_revision(
        self,
        quotation_id: uuid.UUID,
        revision_id: uuid.UUID,
        actor_user: User,
        remarks: str | None,
    ) -> QuotationRevision:
        revision, approval, quotation = self._get_revision_with_approval(quotation_id, revision_id)

        if revision.submitted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="revision already submitted",
            )

        revision.submitted_at = now_utc()
        quotation.status = "PENDING_APPROVAL"
        quotation.updated_at = now_utc()

        self.db.add(
            AuditEvent(
                actor_user_id=actor_user.id,
                entity_type="quotation_revision",
                entity_id=revision.id,
                action="SUBMIT",
                before_jsonb={"submitted_at": None},
                after_jsonb={"submitted_at": revision.submitted_at.isoformat(), "remarks": remarks},
                request_id=get_request_id(),
            )
        )

        self._commit()
        return self.get_revision(quotation_id, revision_id)

    def approve_revision(
        self,
        quotation_id: uuid.UUID,
        revision_id: uuid.UUID,
        actor_user: User,
        remarks: str | None,
    ) -> QuotationRevision:
        revision, approval, quotation = self._get_revision_with_approval(quotation_id, revision_id)

        if revision.submitted_at is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="revision must be submitted before approval",
            )

        if approval.decision != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="approval decision already recorded",
            )

        approved_at = now_utc()
        approval.decision = "APPROVED"
        approval.decided_by = actor_user.id
        approval.decided_at = approved_at
        approval.remarks = remarks

        revision.approved_at = approved_at
        revision.rejected_at = None

        quotation.status = "APPROVED"
        quotation.current_revision_no = revision.revision_no
        quotation.updated_at = approved_at

        self.db.add(
            AuditEvent(
                actor_user_id=actor_user.id,
                entity_type="approval",
                entity_id=approval.id,
                action="APPROVE",
                before_jsonb={"decision": "PENDING"},
                after_jsonb={"decision": "APPROVED", "remarks": remarks},
                request_id=get_request_id(),
            )
        )

        self._commit()
        return self.get_revision(quotation_id, revision_id)

    def reject_revision(
        self,
        quotation_id: uuid.UUID,
        revision_id: uuid.UUID,
        actor_user: User,
        remarks: str | None,
    ) -> QuotationRevision:
        revision, approval, quotation = self._get_revision_with_approval(quotation_id, revision_id)

        if revision.submitted_at is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="revision must be submitted before rejection",
            )

        if approval.decision != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="approval decision already recorded",
            )

        rejected_at = now_utc()
        approval.decision = "REJECTED"
        approval.decided_by = actor_user.id
        approval.decided_at = rejected_at
        approval.remarks = remarks

        revision.rejected_at = rejected_at
        revision.approved_at = None

        quotation.status = "REJECTED"
        quotation.updated_at = rejected_at

        self.db.add(
            AuditEvent(
                actor_user_id=actor_user.id,
                entity_type="approval",
                entity_id=approval.id,
                action="REJECT",
                before_jsonb={"decision": "PENDING"},
                after_jsonb={"decision": "REJECTED", "remarks": remarks},
                request_id=get_request_id(),
            )
        )

        self._commit()
        return self.get_revision(quotation_id, revision_id)

    @staticmethod
    def _calculate_subtotal(payload: QuotationRevisionCreateRequest) -> Decimal:
        subtotal = Decimal("0")
        for item in payload.items:
            subtotal += item.qty * item.unit_price
        return QuotationService._quantize(subtotal)

    @staticmethod
    def _calculate_total(
        subtotal: Decimal,
        freight: Decimal,
        markup_percent: Decimal,
    ) -> Decimal:
        markup_value = subtotal * (markup_percent / Decimal("100"))
        return QuotationService._quantize(subtotal + freight + markup_value)

    @staticmethod
    def _quantize(value: Decimal) -> Decimal:
        return value.quantize(DECIMAL_TWO, rounding=ROUND_HALF_UP)

    def _validate_revision_items(
        self,
        enquiry_id: uuid.UUID,
        payload: QuotationRevisionCreateRequest,
    ) -> None:
        product_ids = {item.product_id for item in payload.items}
        existing_product_ids = set(
            self.db.scalars(select(Product.id).where(Product.id.in_(product_ids)))
        )

        missing_products = sorted(str(pid) for pid in product_ids - existing_product_ids)
        if missing_products:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"unknown product_id values: {', '.join(missing_products)}",
            )

        enquiry_item_ids = {
            item.enquiry_item_id for item in payload.items if item.enquiry_item_id is not None
        }
        if enquiry_item_ids:
            rows = self.db.execute(
                select(EnquiryItem.id, EnquiryItem.enquiry_id).where(
                    EnquiryItem.id.in_(enquiry_item_ids)
                )
            ).all()
            found_ids = {row[0] for row in rows}
            missing = sorted(str(item_id) for item_id in enquiry_item_ids - found_ids)
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"unknown enquiry_item_id values: {', '.join(missing)}",
                )

            wrong_scope = sorted(str(row[0]) for row in rows if row[1] != enquiry_id)
            if wrong_scope:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "enquiry_item_id values do not belong to quotation enquiry: "
                        f"{', '.join(wrong_scope)}"
                    ),
                )

    def _next_revision_no(self, quotation_id: uuid.UUID) -> int:
        current = self.db.scalar(
            select(func.max(QuotationRevision.revision_no)).where(
                QuotationRevision.quotation_id == quotation_id
            )
        )
        return int(current or 0) + 1

    def _has_pending_submitted_revision(self, quotation_id: uuid.UUID) -> bool:
        pending = self.db.scalar(
            select(QuotationRevision.id)
            .join(Approval, Approval.revision_id == QuotationRevision.id)
            .where(
                QuotationRevision.quotation_id == quotation_id,
                QuotationRevision.submitted_at.is_not(None),
                QuotationRevision.approved_at.is_(None),
                QuotationRevision.rejected_at.is_(None),
                Approval.step_name == "FINAL",
                Approval.decision == "PENDING",
            )
            .limit(1)
        )
        return pending is not None

    def _get_quotation_or_404(self, quotation_id: uuid.UUID) -> Quotation:
        quotation = self.db.get(Quotation, quotation_id)
        if quotation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="quotation not found")
        return quotation

    def _get_revision_with_approval(
        self,
        quotation_id: uuid.UUID,
        revision_id: uuid.UUID,
    ) -> tuple[QuotationRevision, Approval, Quotation]:
        revision = self.db.scalar(
            select(QuotationRevision)
            .options(selectinload(QuotationRevision.approvals))
            .where(
                QuotationRevision.id == revision_id,
                QuotationRevision.quotation_id == quotation_id,
            )
        )
        if revision is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="quotation revision not found",
            )

        approval = next((item for item in revision.approvals if item.step_name == "FINAL"), None)
        if approval is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="revision approval workflow is not initialized",
            )

        quotation = self._get_quotation_or_404(quotation_id)
        return revision, approval, quotation

    def _generate_quotation_no(self) -> str:
        now = now_utc()
        suffix = secrets.token_hex(2).upper()
        return f"QT-{now:%Y%m%d-%H%M%S}-{suffix}"

    def _commit(self) -> None:
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc.orig),
            ) from exc
