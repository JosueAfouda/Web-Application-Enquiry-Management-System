from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class QuotationStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApprovalDecision(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class QuotationCreateRequest(BaseModel):
    quotation_no: str | None = Field(default=None, min_length=1, max_length=80)


class QuotationRevisionItemCreate(BaseModel):
    product_id: uuid.UUID
    qty: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    enquiry_item_id: uuid.UUID | None = None
    notes: str | None = None


class QuotationRevisionCreateRequest(BaseModel):
    freight: Decimal = Field(default=Decimal("0"), ge=0)
    markup_percent: Decimal = Field(default=Decimal("0"), ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    items: list[QuotationRevisionItemCreate] = Field(min_length=1)


class QuotationActionRequest(BaseModel):
    remarks: str | None = None


class QuotationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    enquiry_id: uuid.UUID
    quotation_no: str
    current_revision_no: int
    status: QuotationStatus
    created_at: datetime
    updated_at: datetime


class QuotationItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    revision_id: uuid.UUID
    enquiry_item_id: uuid.UUID | None
    product_id: uuid.UUID
    qty: Decimal
    unit_price: Decimal
    line_total: Decimal
    notes: str | None


class ApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    revision_id: uuid.UUID
    step_name: str
    decision: ApprovalDecision
    decided_by: uuid.UUID | None
    decided_at: datetime | None
    remarks: str | None
    created_at: datetime


class QuotationRevisionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    quotation_id: uuid.UUID
    revision_no: int
    freight: Decimal
    markup_percent: Decimal
    subtotal: Decimal
    total: Decimal
    currency: str
    submitted_at: datetime | None
    approved_at: datetime | None
    rejected_at: datetime | None
    created_by: uuid.UUID
    created_at: datetime
    items: list[QuotationItemRead]
    approvals: list[ApprovalRead]


class QuotationDetailRead(QuotationRead):
    revisions: list[QuotationRevisionRead]
