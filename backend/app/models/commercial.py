from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import ENUM, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.enquiry import Enquiry
    from app.models.manufacturer import Manufacturer
    from app.models.quotation import QuotationRevision
    from app.models.user import User

PO_STATUS_VALUES = (
    "DRAFT",
    "ISSUED",
    "CONFIRMED",
    "CLOSED",
    "CANCELLED",
)

INVOICE_STATUS_VALUES = (
    "UNPAID",
    "PARTIAL",
    "PAID",
    "VOID",
)

DELIVERY_STATUS_VALUES = (
    "PENDING",
    "IN_TRANSIT",
    "DELIVERED",
    "FAILED",
    "CANCELLED",
)


class CustomerPO(Base):
    __tablename__ = "customer_pos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    po_no: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    enquiry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enquiries.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quotation_revision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quotation_revisions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    po_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE"),
        index=True,
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        ENUM(*PO_STATUS_VALUES, name="po_status_enum", create_type=False),
        nullable=False,
        server_default=text("'ISSUED'"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    enquiry: Mapped[Enquiry] = relationship(lazy="selectin")
    quotation_revision: Mapped[QuotationRevision] = relationship(lazy="selectin")


class RTMPO(Base):
    __tablename__ = "rtm_pos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    po_no: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    enquiry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enquiries.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quotation_revision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quotation_revisions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    manufacturer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("manufacturers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    po_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE"),
        index=True,
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        ENUM(*PO_STATUS_VALUES, name="po_status_enum", create_type=False),
        nullable=False,
        server_default=text("'ISSUED'"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    enquiry: Mapped[Enquiry] = relationship(lazy="selectin")
    quotation_revision: Mapped[QuotationRevision] = relationship(lazy="selectin")
    manufacturer: Mapped[Manufacturer | None] = relationship(lazy="selectin")


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    invoice_no: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    enquiry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enquiries.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    customer_po_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_pos.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    issue_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE"),
        index=True,
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default=text("'USD'"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        ENUM(*INVOICE_STATUS_VALUES, name="invoice_status_enum", create_type=False),
        nullable=False,
        server_default=text("'UNPAID'"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    enquiry: Mapped[Enquiry] = relationship(lazy="selectin")
    customer_po: Mapped[CustomerPO | None] = relationship(lazy="selectin")
    payments: Mapped[list[Payment]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    payment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=text("CURRENT_DATE"),
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    method: Mapped[str] = mapped_column(String(80), nullable=False)
    reference_no: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    invoice: Mapped[Invoice] = relationship(back_populates="payments", lazy="selectin")


class Delivery(Base):
    __tablename__ = "deliveries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    enquiry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enquiries.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    invoice_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    shipment_no: Mapped[str | None] = mapped_column(String(80), unique=True, nullable=True)
    courier_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tracking_no: Mapped[str | None] = mapped_column(String(120), nullable=True)
    shipped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expected_delivery_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        ENUM(*DELIVERY_STATUS_VALUES, name="delivery_status_enum", create_type=False),
        nullable=False,
        server_default=text("'PENDING'"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    enquiry: Mapped[Enquiry] = relationship(lazy="selectin")
    invoice: Mapped[Invoice | None] = relationship(lazy="selectin")
    events: Mapped[list[DeliveryEvent]] = relationship(
        back_populates="delivery",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class DeliveryEvent(Base):
    __tablename__ = "delivery_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    delivery_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("deliveries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    details_jsonb: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    delivery: Mapped[Delivery] = relationship(back_populates="events", lazy="selectin")
    actor: Mapped[User | None] = relationship(lazy="selectin")
