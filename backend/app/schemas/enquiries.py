from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class EnquiryStatus(str, Enum):
    RECEIVED = "RECEIVED"
    IN_REVIEW = "IN_REVIEW"
    QUOTED = "QUOTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PO_CREATED = "PO_CREATED"
    INVOICED = "INVOICED"
    IN_DELIVERY = "IN_DELIVERY"
    DELIVERED = "DELIVERED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class EnquiryItemCreate(BaseModel):
    product_id: uuid.UUID
    requested_qty: Decimal = Field(gt=0)
    target_price: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None


class EnquiryCreate(BaseModel):
    customer_id: uuid.UUID
    received_date: date | None = None
    currency: str = Field(default="USD", min_length=3, max_length=3)
    notes: str | None = None
    items: list[EnquiryItemCreate] = Field(min_length=1)


class EnquiryItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    requested_qty: Decimal
    target_price: Decimal | None
    notes: str | None
    created_at: datetime


class EnquiryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    enquiry_no: str
    customer_id: uuid.UUID
    owner_user_id: uuid.UUID
    status: EnquiryStatus
    received_date: date
    currency: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
    items: list[EnquiryItemRead]


class EnquiryStatusTransitionRequest(BaseModel):
    to_status: EnquiryStatus
    comment: str | None = None


class EnquiryStatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    enquiry_id: uuid.UUID
    from_status: EnquiryStatus | None
    to_status: EnquiryStatus
    changed_by: uuid.UUID
    changed_at: datetime
    comment: str | None
