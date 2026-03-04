from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class DateRangeRead(BaseModel):
    date_from: date | None
    date_to: date | None


class EnquiryCountByStatus(BaseModel):
    status: str
    count: int


class QuotationApprovalKPI(BaseModel):
    approved_count: int
    decided_count: int
    approval_rate: float


class POConversionKPI(BaseModel):
    enquiries_with_po: int
    total_enquiries: int
    conversion_rate: float


class InvoiceCollectionKPI(BaseModel):
    invoiced_total: Decimal
    collected_total: Decimal
    outstanding_total: Decimal


class DeliveryCompletionKPI(BaseModel):
    delivered_count: int
    total_deliveries: int
    completion_rate: float


class KPIReportRead(BaseModel):
    window: DateRangeRead
    enquiry_counts_by_status: list[EnquiryCountByStatus]
    quotation_approval: QuotationApprovalKPI
    po_conversion: POConversionKPI
    invoice_collection: InvoiceCollectionKPI
    delivery_completion: DeliveryCompletionKPI
