from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.enquiry import Enquiry, EnquiryItem
    from app.models.product import Product
    from app.models.user import User

QUOTATION_STATUS_VALUES = (
    "DRAFT",
    "PENDING_APPROVAL",
    "APPROVED",
    "REJECTED",
)

APPROVAL_DECISION_VALUES = (
    "PENDING",
    "APPROVED",
    "REJECTED",
)


class Quotation(Base):
    __tablename__ = "quotations"

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
    quotation_no: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    current_revision_no: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
    status: Mapped[str] = mapped_column(
        ENUM(*QUOTATION_STATUS_VALUES, name="quotation_status_enum", create_type=False),
        nullable=False,
        server_default=text("'DRAFT'"),
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
    revisions: Mapped[list[QuotationRevision]] = relationship(
        back_populates="quotation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class QuotationRevision(Base):
    __tablename__ = "quotation_revisions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    quotation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quotations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    revision_no: Mapped[int] = mapped_column(Integer, nullable=False)
    freight: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        server_default=text("0"),
    )
    markup_percent: Mapped[Decimal] = mapped_column(
        Numeric(6, 3),
        nullable=False,
        server_default=text("0"),
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        server_default=text("0"),
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        server_default=text("0"),
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default=text("'USD'"))
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    quotation: Mapped[Quotation] = relationship(back_populates="revisions", lazy="selectin")
    creator: Mapped[User] = relationship(lazy="selectin")
    items: Mapped[list[QuotationItem]] = relationship(
        back_populates="revision",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    approvals: Mapped[list[Approval]] = relationship(
        back_populates="revision",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class QuotationItem(Base):
    __tablename__ = "quotation_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    revision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quotation_revisions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    enquiry_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enquiry_items.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    qty: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    revision: Mapped[QuotationRevision] = relationship(back_populates="items", lazy="selectin")
    enquiry_item: Mapped[EnquiryItem | None] = relationship(lazy="selectin")
    product: Mapped[Product] = relationship(lazy="selectin")


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    revision_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quotation_revisions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    step_name: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        server_default=text("'FINAL'"),
    )
    decision: Mapped[str] = mapped_column(
        ENUM(*APPROVAL_DECISION_VALUES, name="approval_decision_enum", create_type=False),
        nullable=False,
        server_default=text("'PENDING'"),
    )
    decided_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    revision: Mapped[QuotationRevision] = relationship(back_populates="approvals", lazy="selectin")
    decider: Mapped[User | None] = relationship(lazy="selectin")
