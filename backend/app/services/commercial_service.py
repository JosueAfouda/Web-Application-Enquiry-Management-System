from __future__ import annotations

import secrets
import uuid
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import Settings
from app.core.request_context import get_request_id
from app.core.security import now_utc
from app.models.audit_event import AuditEvent
from app.models.commercial import (
    RTMPO,
    CustomerPO,
    Delivery,
    DeliveryEvent,
    Invoice,
    Payment,
)
from app.models.enquiry import Enquiry
from app.models.manufacturer import Manufacturer
from app.models.quotation import Quotation, QuotationRevision
from app.models.user import User
from app.schemas.commercial import (
    CustomerPOCreateRequest,
    DeliveryCreateRequest,
    DeliveryEventCreateRequest,
    DeliveryStatus,
    InvoiceCreateRequest,
    PaymentCreateRequest,
    RTMPOCreateRequest,
)

DECIMAL_TWO = Decimal("0.01")


class CommercialService:
    def __init__(self, db: Session, settings: Settings):
        self.db = db
        self.settings = settings

    def create_customer_po(
        self,
        quotation_id: uuid.UUID,
        revision_id: uuid.UUID,
        payload: CustomerPOCreateRequest,
        actor_user: User,
    ) -> CustomerPO:
        revision, _, enquiry = self._validated_revision_for_po(quotation_id, revision_id)

        po = CustomerPO(
            po_no=(payload.po_no.strip() if payload.po_no else self._generate_po_no("CPO")),
            enquiry_id=enquiry.id,
            quotation_revision_id=revision.id,
            customer_id=enquiry.customer_id,
            po_date=payload.po_date or date.today(),
            total_amount=self._quantize(payload.total_amount or revision.total),
            status=payload.status.value,
        )
        self.db.add(po)
        self.db.flush()

        self.db.add(
            AuditEvent(
                actor_user_id=actor_user.id,
                entity_type="customer_po",
                entity_id=po.id,
                action="CREATE",
                before_jsonb={},
                after_jsonb={
                    "po_no": po.po_no,
                    "quotation_revision_id": str(revision.id),
                    "total_amount": str(po.total_amount),
                },
                request_id=get_request_id(),
            )
        )

        self._commit()
        return self.get_customer_po(po.id)

    def create_rtm_po(
        self,
        quotation_id: uuid.UUID,
        revision_id: uuid.UUID,
        payload: RTMPOCreateRequest,
        actor_user: User,
    ) -> RTMPO:
        revision, _, enquiry = self._validated_revision_for_po(quotation_id, revision_id)

        if (
            payload.manufacturer_id is not None
            and self.db.get(
                Manufacturer,
                payload.manufacturer_id,
            )
            is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="manufacturer_id does not exist",
            )

        po = RTMPO(
            po_no=(payload.po_no.strip() if payload.po_no else self._generate_po_no("RPO")),
            enquiry_id=enquiry.id,
            quotation_revision_id=revision.id,
            manufacturer_id=payload.manufacturer_id,
            po_date=payload.po_date or date.today(),
            total_amount=self._quantize(payload.total_amount or revision.total),
            status=payload.status.value,
        )
        self.db.add(po)
        self.db.flush()

        self.db.add(
            AuditEvent(
                actor_user_id=actor_user.id,
                entity_type="rtm_po",
                entity_id=po.id,
                action="CREATE",
                before_jsonb={},
                after_jsonb={
                    "po_no": po.po_no,
                    "quotation_revision_id": str(revision.id),
                    "manufacturer_id": str(po.manufacturer_id) if po.manufacturer_id else None,
                    "total_amount": str(po.total_amount),
                },
                request_id=get_request_id(),
            )
        )

        self._commit()
        return self.get_rtm_po(po.id)

    def create_invoice(self, payload: InvoiceCreateRequest, actor_user: User) -> Invoice:
        enquiry = self.db.get(Enquiry, payload.enquiry_id)
        if enquiry is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="enquiry_id does not exist",
            )

        customer_po = None
        if payload.customer_po_id is not None:
            customer_po = self.db.get(CustomerPO, payload.customer_po_id)
            if customer_po is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="customer_po_id does not exist",
                )
            if customer_po.enquiry_id != enquiry.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="customer_po_id does not belong to enquiry_id",
                )

        total_amount: Decimal
        if payload.total_amount is not None:
            total_amount = payload.total_amount
        elif customer_po is not None:
            total_amount = customer_po.total_amount
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="total_amount is required when customer_po_id is not provided",
            )

        issue_date_value = payload.issue_date or date.today()
        due_date_value = payload.due_date
        if due_date_value is not None and due_date_value < issue_date_value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="due_date cannot be before issue_date",
            )

        invoice = Invoice(
            invoice_no=(
                payload.invoice_no.strip() if payload.invoice_no else self._generate_invoice_no()
            ),
            enquiry_id=enquiry.id,
            customer_po_id=payload.customer_po_id,
            issue_date=issue_date_value,
            due_date=due_date_value,
            currency=payload.currency.upper(),
            total_amount=self._quantize(total_amount),
            status="UNPAID",
        )
        self.db.add(invoice)
        self.db.flush()

        self.db.add(
            AuditEvent(
                actor_user_id=actor_user.id,
                entity_type="invoice",
                entity_id=invoice.id,
                action="CREATE",
                before_jsonb={},
                after_jsonb={
                    "invoice_no": invoice.invoice_no,
                    "enquiry_id": str(invoice.enquiry_id),
                    "status": invoice.status,
                    "total_amount": str(invoice.total_amount),
                },
                request_id=get_request_id(),
            )
        )

        self._commit()
        return self.get_invoice(invoice.id)

    def create_payment(self, payload: PaymentCreateRequest, actor_user: User) -> Payment:
        invoice = self.db.get(Invoice, payload.invoice_id)
        if invoice is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="invoice_id does not exist",
            )

        already_paid = self.db.scalar(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.invoice_id == invoice.id
            )
        )
        paid_before = Decimal(str(already_paid))
        paid_after = self._quantize(paid_before + payload.amount)
        invoice_total = self._quantize(invoice.total_amount)
        if paid_after > invoice_total:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="payment exceeds invoice total amount",
            )

        payment = Payment(
            invoice_id=invoice.id,
            payment_date=payload.payment_date or date.today(),
            amount=self._quantize(payload.amount),
            method=payload.method.strip(),
            reference_no=(payload.reference_no.strip() if payload.reference_no else None),
            notes=payload.notes,
        )
        self.db.add(payment)
        self.db.flush()

        previous_status = invoice.status
        invoice.status = self.derive_invoice_status(invoice_total, paid_after)
        invoice.updated_at = now_utc()

        self.db.add(
            AuditEvent(
                actor_user_id=actor_user.id,
                entity_type="payment",
                entity_id=payment.id,
                action="CREATE",
                before_jsonb={"invoice_status": previous_status},
                after_jsonb={
                    "invoice_id": str(invoice.id),
                    "paid_after": str(paid_after),
                    "invoice_status": invoice.status,
                },
                request_id=get_request_id(),
            )
        )

        self._commit()
        return self.get_payment(payment.id)

    def create_delivery(self, payload: DeliveryCreateRequest, actor_user: User) -> Delivery:
        enquiry = self.db.get(Enquiry, payload.enquiry_id)
        if enquiry is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="enquiry_id does not exist",
            )

        if payload.invoice_id is not None:
            invoice = self.db.get(Invoice, payload.invoice_id)
            if invoice is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="invoice_id does not exist",
                )
            if invoice.enquiry_id != enquiry.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="invoice_id does not belong to enquiry_id",
                )

        self._ensure_delivery_prerequisite(enquiry.id)

        delivery = Delivery(
            enquiry_id=enquiry.id,
            invoice_id=payload.invoice_id,
            shipment_no=(
                payload.shipment_no.strip() if payload.shipment_no else self._generate_shipment_no()
            ),
            courier_name=(payload.courier_name.strip() if payload.courier_name else None),
            tracking_no=(payload.tracking_no.strip() if payload.tracking_no else None),
            shipped_at=payload.shipped_at,
            expected_delivery_at=payload.expected_delivery_at,
            delivered_at=payload.delivered_at,
            status=self._resolve_delivery_status(payload),
        )
        self.db.add(delivery)
        self.db.flush()

        self.db.add(
            AuditEvent(
                actor_user_id=actor_user.id,
                entity_type="delivery",
                entity_id=delivery.id,
                action="CREATE",
                before_jsonb={},
                after_jsonb={
                    "shipment_no": delivery.shipment_no,
                    "status": delivery.status,
                    "enquiry_id": str(delivery.enquiry_id),
                },
                request_id=get_request_id(),
            )
        )

        self._commit()
        return self.get_delivery(delivery.id)

    def add_delivery_event(
        self,
        delivery_id: uuid.UUID,
        payload: DeliveryEventCreateRequest,
        actor_user: User,
    ) -> DeliveryEvent:
        delivery = self.db.get(Delivery, delivery_id)
        if delivery is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="delivery not found",
            )

        event_time = payload.event_time or now_utc()
        latest_event_time = self.db.scalar(
            select(func.max(DeliveryEvent.event_time)).where(
                DeliveryEvent.delivery_id == delivery.id
            )
        )
        if latest_event_time is not None and event_time < latest_event_time:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="event_time cannot be older than existing delivery timeline events",
            )

        event_type = payload.event_type.strip().upper()
        event = DeliveryEvent(
            delivery_id=delivery.id,
            event_type=event_type,
            event_time=event_time,
            location=(payload.location.strip() if payload.location else None),
            details_jsonb=payload.details_jsonb,
            created_by=actor_user.id,
        )
        self.db.add(event)
        self.db.flush()

        if event_type in {"SHIPPED", "IN_TRANSIT"}:
            delivery.status = DeliveryStatus.IN_TRANSIT.value
            delivery.shipped_at = delivery.shipped_at or event_time
            delivery.updated_at = now_utc()
        if event_type == "DELIVERED":
            delivery.status = DeliveryStatus.DELIVERED.value
            delivery.delivered_at = delivery.delivered_at or event_time
            delivery.updated_at = now_utc()

        self.db.add(
            AuditEvent(
                actor_user_id=actor_user.id,
                entity_type="delivery_event",
                entity_id=event.id,
                action="CREATE",
                before_jsonb={},
                after_jsonb={
                    "delivery_id": str(delivery.id),
                    "event_type": event_type,
                    "event_time": event.event_time.isoformat(),
                },
                request_id=get_request_id(),
            )
        )

        self._commit()
        return self.get_delivery_event(event.id)

    def get_customer_po(self, po_id: uuid.UUID) -> CustomerPO:
        customer_po = self.db.get(CustomerPO, po_id)
        if customer_po is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="customer po not found",
            )
        return customer_po

    def get_rtm_po(self, po_id: uuid.UUID) -> RTMPO:
        rtm_po = self.db.get(RTMPO, po_id)
        if rtm_po is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="rtm po not found",
            )
        return rtm_po

    def get_invoice(self, invoice_id: uuid.UUID) -> Invoice:
        invoice = self.db.scalar(
            select(Invoice).options(selectinload(Invoice.payments)).where(Invoice.id == invoice_id)
        )
        if invoice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="invoice not found",
            )
        invoice.payments.sort(key=lambda payment: payment.created_at)
        return invoice

    def get_payment(self, payment_id: uuid.UUID) -> Payment:
        payment = self.db.get(Payment, payment_id)
        if payment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="payment not found",
            )
        return payment

    def get_delivery(self, delivery_id: uuid.UUID) -> Delivery:
        delivery = self.db.scalar(
            select(Delivery)
            .options(selectinload(Delivery.events))
            .where(Delivery.id == delivery_id)
        )
        if delivery is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="delivery not found",
            )
        delivery.events.sort(key=lambda event: (event.event_time, event.created_at))
        return delivery

    def get_delivery_event(self, event_id: uuid.UUID) -> DeliveryEvent:
        event = self.db.get(DeliveryEvent, event_id)
        if event is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="delivery event not found",
            )
        return event

    def _validated_revision_for_po(
        self,
        quotation_id: uuid.UUID,
        revision_id: uuid.UUID,
    ) -> tuple[QuotationRevision, Quotation, Enquiry]:
        revision = self.db.scalar(
            select(QuotationRevision)
            .options(selectinload(QuotationRevision.quotation))
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

        if revision.approved_at is None or revision.rejected_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="only approved revisions can generate purchase orders",
            )

        quotation = revision.quotation
        enquiry = self.db.get(Enquiry, quotation.enquiry_id)
        if enquiry is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="enquiry not found",
            )
        return revision, quotation, enquiry

    def _ensure_delivery_prerequisite(self, enquiry_id: uuid.UUID) -> None:
        required_step = self.settings.delivery_start_required_step
        if required_step == "PO_CREATED":
            has_customer_po = self.db.scalar(
                select(CustomerPO.id).where(CustomerPO.enquiry_id == enquiry_id).limit(1)
            )
            has_rtm_po = self.db.scalar(
                select(RTMPO.id).where(RTMPO.enquiry_id == enquiry_id).limit(1)
            )
            if has_customer_po is None and has_rtm_po is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="delivery requires PO_CREATED commercial step",
                )
            return

        has_invoice = self.db.scalar(
            select(Invoice.id).where(Invoice.enquiry_id == enquiry_id).limit(1)
        )
        if has_invoice is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="delivery requires INVOICED commercial step",
            )

    @staticmethod
    def derive_invoice_status(total_amount: Decimal, paid_amount: Decimal) -> str:
        total = CommercialService._quantize(total_amount)
        paid = CommercialService._quantize(paid_amount)
        if paid <= Decimal("0"):
            return "UNPAID"
        if paid < total:
            return "PARTIAL"
        return "PAID"

    @staticmethod
    def _resolve_delivery_status(payload: DeliveryCreateRequest) -> str:
        if payload.delivered_at is not None:
            return DeliveryStatus.DELIVERED.value
        if payload.shipped_at is not None and payload.status == DeliveryStatus.PENDING:
            return DeliveryStatus.IN_TRANSIT.value
        return payload.status.value

    @staticmethod
    def _quantize(value: Decimal) -> Decimal:
        return value.quantize(DECIMAL_TWO, rounding=ROUND_HALF_UP)

    def _generate_po_no(self, prefix: str) -> str:
        now = now_utc()
        suffix = secrets.token_hex(2).upper()
        return f"{prefix}-{now:%Y%m%d-%H%M%S}-{suffix}"

    def _generate_invoice_no(self) -> str:
        now = now_utc()
        suffix = secrets.token_hex(2).upper()
        return f"INV-{now:%Y%m%d-%H%M%S}-{suffix}"

    def _generate_shipment_no(self) -> str:
        now = now_utc()
        suffix = secrets.token_hex(2).upper()
        return f"SHP-{now:%Y%m%d-%H%M%S}-{suffix}"

    def _commit(self) -> None:
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc.orig),
            ) from exc
