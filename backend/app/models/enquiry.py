from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.product import Product
    from app.models.user import User

ENQUIRY_STATUS_VALUES = (
    "RECEIVED",
    "IN_REVIEW",
    "QUOTED",
    "PENDING_APPROVAL",
    "APPROVED",
    "REJECTED",
    "PO_CREATED",
    "INVOICED",
    "IN_DELIVERY",
    "DELIVERED",
    "CLOSED",
    "CANCELLED",
)


class Enquiry(Base):
    __tablename__ = "enquiries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    enquiry_no: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        ENUM(*ENQUIRY_STATUS_VALUES, name="enquiry_status_enum", create_type=False),
        nullable=False,
        server_default=text("'RECEIVED'"),
        index=True,
    )
    received_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
        index=True,
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default=text("'USD'"))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    customer: Mapped[Customer] = relationship(lazy="selectin")
    owner: Mapped[User] = relationship(lazy="selectin")
    items: Mapped[list[EnquiryItem]] = relationship(
        back_populates="enquiry",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    history: Mapped[list[EnquiryStatusHistory]] = relationship(
        back_populates="enquiry",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class EnquiryItem(Base):
    __tablename__ = "enquiry_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    enquiry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enquiries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    requested_qty: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    target_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    enquiry: Mapped[Enquiry] = relationship(back_populates="items", lazy="selectin")
    product: Mapped[Product] = relationship(lazy="selectin")


class EnquiryStatusHistory(Base):
    __tablename__ = "enquiry_status_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    enquiry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("enquiries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_status: Mapped[str | None] = mapped_column(
        ENUM(*ENQUIRY_STATUS_VALUES, name="enquiry_status_enum", create_type=False),
        nullable=True,
    )
    to_status: Mapped[str] = mapped_column(
        ENUM(*ENQUIRY_STATUS_VALUES, name="enquiry_status_enum", create_type=False),
        nullable=False,
    )
    changed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    enquiry: Mapped[Enquiry] = relationship(back_populates="history", lazy="selectin")
    actor: Mapped[User] = relationship(lazy="selectin")
