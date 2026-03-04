from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class POStatus(str, Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    CONFIRMED = "CONFIRMED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class InvoiceStatus(str, Enum):
    UNPAID = "UNPAID"
    PARTIAL = "PARTIAL"
    PAID = "PAID"
    VOID = "VOID"


class DeliveryStatus(str, Enum):
    PENDING = "PENDING"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class CustomerPOCreateRequest(BaseModel):
    po_no: str | None = Field(default=None, min_length=1, max_length=80)
    po_date: date | None = None
    total_amount: Decimal | None = Field(default=None, ge=0)
    status: POStatus = POStatus.ISSUED


class RTMPOCreateRequest(BaseModel):
    po_no: str | None = Field(default=None, min_length=1, max_length=80)
    manufacturer_id: uuid.UUID | None = None
    po_date: date | None = None
    total_amount: Decimal | None = Field(default=None, ge=0)
    status: POStatus = POStatus.ISSUED


class InvoiceCreateRequest(BaseModel):
    invoice_no: str | None = Field(default=None, min_length=1, max_length=80)
    enquiry_id: uuid.UUID
    customer_po_id: uuid.UUID | None = None
    issue_date: date | None = None
    due_date: date | None = None
    currency: str = Field(default="USD", min_length=3, max_length=3)
    total_amount: Decimal | None = Field(default=None, ge=0)


class PaymentCreateRequest(BaseModel):
    invoice_id: uuid.UUID
    payment_date: date | None = None
    amount: Decimal = Field(gt=0)
    method: str = Field(min_length=1, max_length=80)
    reference_no: str | None = Field(default=None, max_length=120)
    notes: str | None = None


class DeliveryCreateRequest(BaseModel):
    enquiry_id: uuid.UUID
    invoice_id: uuid.UUID | None = None
    shipment_no: str | None = Field(default=None, min_length=1, max_length=80)
    courier_name: str | None = Field(default=None, max_length=120)
    tracking_no: str | None = Field(default=None, max_length=120)
    shipped_at: datetime | None = None
    expected_delivery_at: datetime | None = None
    delivered_at: datetime | None = None
    status: DeliveryStatus = DeliveryStatus.PENDING


class DeliveryEventCreateRequest(BaseModel):
    event_type: str = Field(min_length=1, max_length=80)
    event_time: datetime | None = None
    location: str | None = Field(default=None, max_length=255)
    details_jsonb: dict[str, Any] = Field(default_factory=dict)


class CustomerPORead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    po_no: str
    enquiry_id: uuid.UUID
    quotation_revision_id: uuid.UUID
    customer_id: uuid.UUID
    po_date: date
    total_amount: Decimal
    status: POStatus
    created_at: datetime
    updated_at: datetime


class RTMPORead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    po_no: str
    enquiry_id: uuid.UUID
    quotation_revision_id: uuid.UUID
    manufacturer_id: uuid.UUID | None
    po_date: date
    total_amount: Decimal
    status: POStatus
    created_at: datetime
    updated_at: datetime


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    invoice_id: uuid.UUID
    payment_date: date
    amount: Decimal
    method: str
    reference_no: str | None
    notes: str | None
    created_at: datetime


class InvoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    invoice_no: str
    enquiry_id: uuid.UUID
    customer_po_id: uuid.UUID | None
    issue_date: date
    due_date: date | None
    currency: str
    total_amount: Decimal
    status: InvoiceStatus
    created_at: datetime
    updated_at: datetime
    payments: list[PaymentRead] = Field(default_factory=list)


class DeliveryEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    delivery_id: uuid.UUID
    event_type: str
    event_time: datetime
    location: str | None
    details_jsonb: dict[str, Any]
    created_by: uuid.UUID | None
    created_at: datetime


class DeliveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    enquiry_id: uuid.UUID
    invoice_id: uuid.UUID | None
    shipment_no: str | None
    courier_name: str | None
    tracking_no: str | None
    shipped_at: datetime | None
    expected_delivery_at: datetime | None
    delivered_at: datetime | None
    status: DeliveryStatus
    created_at: datetime
    updated_at: datetime
    events: list[DeliveryEventRead] = Field(default_factory=list)
