from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from sqlalchemy import Date, cast, distinct, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.commercial import RTMPO, CustomerPO, Delivery, Invoice, Payment
from app.models.enquiry import Enquiry
from app.models.quotation import Approval, Quotation
from app.schemas.reports import (
    DateRangeRead,
    DeliveryCompletionKPI,
    EnquiryCountByStatus,
    InvoiceCollectionKPI,
    KPIReportRead,
    POConversionKPI,
    QuotationApprovalKPI,
)
from app.utils.excel import build_excel_report

DECIMAL_TWO = Decimal("0.01")


class ReportsService:
    def __init__(self, db: Session):
        self.db = db

    def get_kpis(self, *, date_from: date | None, date_to: date | None) -> KPIReportRead:
        enquiry_counts = self._enquiry_counts_by_status(date_from=date_from, date_to=date_to)
        quotation_approval = self._quotation_approval_kpi(date_from=date_from, date_to=date_to)
        po_conversion = self._po_conversion_kpi(date_from=date_from, date_to=date_to)
        invoice_collection = self._invoice_collection_kpi(date_from=date_from, date_to=date_to)
        delivery_completion = self._delivery_completion_kpi(date_from=date_from, date_to=date_to)

        return KPIReportRead(
            window=DateRangeRead(date_from=date_from, date_to=date_to),
            enquiry_counts_by_status=enquiry_counts,
            quotation_approval=quotation_approval,
            po_conversion=po_conversion,
            invoice_collection=invoice_collection,
            delivery_completion=delivery_completion,
        )

    def export_enquiries(
        self,
        *,
        date_from: date | None,
        date_to: date | None,
        status: str | None,
    ) -> bytes:
        stmt = (
            select(Enquiry).options(selectinload(Enquiry.items)).order_by(Enquiry.created_at.desc())
        )
        stmt = self._apply_date_filters_date(
            stmt,
            Enquiry.received_date,
            date_from=date_from,
            date_to=date_to,
        )
        if status is not None:
            stmt = stmt.where(Enquiry.status == status)

        enquiries = list(self.db.scalars(stmt))
        rows = [
            {
                "enquiry_no": enquiry.enquiry_no,
                "status": enquiry.status,
                "customer_id": str(enquiry.customer_id),
                "owner_user_id": str(enquiry.owner_user_id),
                "received_date": enquiry.received_date.isoformat(),
                "currency": enquiry.currency,
                "item_count": len(enquiry.items),
                "created_at": self._dt_to_iso(enquiry.created_at),
            }
            for enquiry in enquiries
        ]
        return build_excel_report(
            rows,
            sheet_name="enquiries",
            columns=[
                "enquiry_no",
                "status",
                "customer_id",
                "owner_user_id",
                "received_date",
                "currency",
                "item_count",
                "created_at",
            ],
        )

    def export_quotations(
        self,
        *,
        date_from: date | None,
        date_to: date | None,
        status: str | None,
    ) -> bytes:
        stmt = (
            select(Quotation, Enquiry.enquiry_no)
            .join(Enquiry, Enquiry.id == Quotation.enquiry_id)
            .order_by(Quotation.created_at.desc())
        )
        stmt = self._apply_date_filters_datetime(
            stmt,
            Quotation.created_at,
            date_from=date_from,
            date_to=date_to,
        )
        if status is not None:
            stmt = stmt.where(Quotation.status == status)

        rows = [
            {
                "quotation_no": quotation.quotation_no,
                "enquiry_no": enquiry_no,
                "status": quotation.status,
                "current_revision_no": quotation.current_revision_no,
                "created_at": self._dt_to_iso(quotation.created_at),
                "updated_at": self._dt_to_iso(quotation.updated_at),
            }
            for quotation, enquiry_no in self.db.execute(stmt).all()
        ]
        return build_excel_report(
            rows,
            sheet_name="quotations",
            columns=[
                "quotation_no",
                "enquiry_no",
                "status",
                "current_revision_no",
                "created_at",
                "updated_at",
            ],
        )

    def export_invoices(
        self,
        *,
        date_from: date | None,
        date_to: date | None,
        status: str | None,
    ) -> bytes:
        stmt = (
            select(Invoice, Enquiry.enquiry_no)
            .join(Enquiry, Enquiry.id == Invoice.enquiry_id)
            .options(selectinload(Invoice.payments))
            .order_by(Invoice.issue_date.desc(), Invoice.created_at.desc())
        )
        stmt = self._apply_date_filters_date(
            stmt,
            Invoice.issue_date,
            date_from=date_from,
            date_to=date_to,
        )
        if status is not None:
            stmt = stmt.where(Invoice.status == status)

        rows: list[dict[str, Any]] = []
        for invoice, enquiry_no in self.db.execute(stmt).all():
            paid_total = self._quantize(
                sum((Decimal(str(payment.amount)) for payment in invoice.payments), Decimal("0"))
            )
            outstanding_total = self._quantize(
                max(Decimal(str(invoice.total_amount)) - paid_total, Decimal("0"))
            )
            rows.append(
                {
                    "invoice_no": invoice.invoice_no,
                    "enquiry_no": enquiry_no,
                    "status": invoice.status,
                    "issue_date": invoice.issue_date.isoformat(),
                    "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                    "currency": invoice.currency,
                    "total_amount": str(self._quantize(Decimal(str(invoice.total_amount)))),
                    "paid_amount": str(paid_total),
                    "outstanding_amount": str(outstanding_total),
                    "created_at": self._dt_to_iso(invoice.created_at),
                }
            )

        return build_excel_report(
            rows,
            sheet_name="invoices",
            columns=[
                "invoice_no",
                "enquiry_no",
                "status",
                "issue_date",
                "due_date",
                "currency",
                "total_amount",
                "paid_amount",
                "outstanding_amount",
                "created_at",
            ],
        )

    def export_payments(
        self,
        *,
        date_from: date | None,
        date_to: date | None,
        method: str | None,
    ) -> bytes:
        stmt = (
            select(Payment, Invoice.invoice_no, Invoice.enquiry_id)
            .join(Invoice, Invoice.id == Payment.invoice_id)
            .order_by(Payment.payment_date.desc(), Payment.created_at.desc())
        )
        stmt = self._apply_date_filters_date(
            stmt,
            Payment.payment_date,
            date_from=date_from,
            date_to=date_to,
        )
        if method is not None:
            stmt = stmt.where(Payment.method == method.strip())

        rows = [
            {
                "invoice_no": invoice_no,
                "enquiry_id": str(enquiry_id),
                "payment_date": payment.payment_date.isoformat(),
                "amount": str(self._quantize(Decimal(str(payment.amount)))),
                "method": payment.method,
                "reference_no": payment.reference_no,
                "notes": payment.notes,
                "created_at": self._dt_to_iso(payment.created_at),
            }
            for payment, invoice_no, enquiry_id in self.db.execute(stmt).all()
        ]
        return build_excel_report(
            rows,
            sheet_name="payments",
            columns=[
                "invoice_no",
                "enquiry_id",
                "payment_date",
                "amount",
                "method",
                "reference_no",
                "notes",
                "created_at",
            ],
        )

    def _enquiry_counts_by_status(
        self,
        *,
        date_from: date | None,
        date_to: date | None,
    ) -> list[EnquiryCountByStatus]:
        stmt = (
            select(Enquiry.status, func.count(Enquiry.id))
            .group_by(Enquiry.status)
            .order_by(Enquiry.status.asc())
        )
        stmt = self._apply_date_filters_date(
            stmt,
            Enquiry.received_date,
            date_from=date_from,
            date_to=date_to,
        )
        return [
            EnquiryCountByStatus(status=status, count=count)
            for status, count in self.db.execute(stmt).all()
        ]

    def _quotation_approval_kpi(
        self,
        *,
        date_from: date | None,
        date_to: date | None,
    ) -> QuotationApprovalKPI:
        stmt = (
            select(Approval.decision, func.count(Approval.id))
            .where(
                Approval.step_name == "FINAL",
                Approval.decided_at.is_not(None),
            )
            .group_by(Approval.decision)
        )
        stmt = self._apply_date_filters_date(
            stmt,
            cast(Approval.decided_at, Date),
            date_from=date_from,
            date_to=date_to,
        )
        decision_counts = {decision: count for decision, count in self.db.execute(stmt).all()}
        approved_count = int(decision_counts.get("APPROVED", 0))
        rejected_count = int(decision_counts.get("REJECTED", 0))
        decided_count = approved_count + rejected_count

        return QuotationApprovalKPI(
            approved_count=approved_count,
            decided_count=decided_count,
            approval_rate=self._safe_ratio(approved_count, decided_count),
        )

    def _po_conversion_kpi(
        self,
        *,
        date_from: date | None,
        date_to: date | None,
    ) -> POConversionKPI:
        enquiry_stmt = select(func.count(Enquiry.id))
        enquiry_stmt = self._apply_date_filters_date(
            enquiry_stmt,
            Enquiry.received_date,
            date_from=date_from,
            date_to=date_to,
        )
        total_enquiries = int(self.db.scalar(enquiry_stmt) or 0)

        customer_po_stmt = select(CustomerPO.enquiry_id.label("enquiry_id"))
        customer_po_stmt = self._apply_date_filters_date(
            customer_po_stmt,
            CustomerPO.po_date,
            date_from=date_from,
            date_to=date_to,
        )

        rtm_po_stmt = select(RTMPO.enquiry_id.label("enquiry_id"))
        rtm_po_stmt = self._apply_date_filters_date(
            rtm_po_stmt,
            RTMPO.po_date,
            date_from=date_from,
            date_to=date_to,
        )

        po_union_subquery = customer_po_stmt.union(rtm_po_stmt).subquery()
        po_enquiries = int(
            self.db.scalar(select(func.count(distinct(po_union_subquery.c.enquiry_id)))) or 0
        )

        return POConversionKPI(
            enquiries_with_po=po_enquiries,
            total_enquiries=total_enquiries,
            conversion_rate=self._safe_ratio(po_enquiries, total_enquiries),
        )

    def _invoice_collection_kpi(
        self,
        *,
        date_from: date | None,
        date_to: date | None,
    ) -> InvoiceCollectionKPI:
        invoice_rows = self.db.execute(
            self._apply_date_filters_date(
                select(Invoice.id, Invoice.total_amount),
                Invoice.issue_date,
                date_from=date_from,
                date_to=date_to,
            )
        ).all()
        invoice_ids = [invoice_id for invoice_id, _ in invoice_rows]
        invoiced_total = self._quantize(
            sum((Decimal(str(total_amount)) for _, total_amount in invoice_rows), Decimal("0"))
        )

        collected_total = Decimal("0")
        if invoice_ids:
            collected_total_raw = self.db.scalar(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.invoice_id.in_(invoice_ids)
                )
            )
            collected_total = self._quantize(Decimal(str(collected_total_raw or 0)))

        outstanding_total = self._quantize(max(invoiced_total - collected_total, Decimal("0")))
        return InvoiceCollectionKPI(
            invoiced_total=invoiced_total,
            collected_total=collected_total,
            outstanding_total=outstanding_total,
        )

    def _delivery_completion_kpi(
        self,
        *,
        date_from: date | None,
        date_to: date | None,
    ) -> DeliveryCompletionKPI:
        stmt = select(Delivery.status, func.count(Delivery.id)).group_by(Delivery.status)
        stmt = self._apply_date_filters_datetime(
            stmt,
            Delivery.created_at,
            date_from=date_from,
            date_to=date_to,
        )
        counts = {status: count for status, count in self.db.execute(stmt).all()}
        delivered_count = int(counts.get("DELIVERED", 0))
        total_deliveries = int(sum(counts.values()))
        return DeliveryCompletionKPI(
            delivered_count=delivered_count,
            total_deliveries=total_deliveries,
            completion_rate=self._safe_ratio(delivered_count, total_deliveries),
        )

    def _apply_date_filters_date(
        self,
        stmt: Any,
        field: Any,
        *,
        date_from: date | None,
        date_to: date | None,
    ) -> Any:
        if date_from is not None:
            stmt = stmt.where(field >= date_from)
        if date_to is not None:
            stmt = stmt.where(field <= date_to)
        return stmt

    def _apply_date_filters_datetime(
        self,
        stmt: Any,
        field: Any,
        *,
        date_from: date | None,
        date_to: date | None,
    ) -> Any:
        if date_from is not None:
            start_dt = datetime.combine(date_from, datetime.min.time(), tzinfo=UTC)
            stmt = stmt.where(field >= start_dt)
        if date_to is not None:
            end_exclusive = datetime.combine(
                date_to + timedelta(days=1),
                datetime.min.time(),
                tzinfo=UTC,
            )
            stmt = stmt.where(field < end_exclusive)
        return stmt

    @staticmethod
    def _safe_ratio(numerator: int, denominator: int) -> float:
        if denominator <= 0:
            return 0.0
        return round(numerator / denominator, 4)

    @staticmethod
    def _dt_to_iso(value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()

    @staticmethod
    def _quantize(value: Decimal) -> Decimal:
        return value.quantize(DECIMAL_TWO, rounding=ROUND_HALF_UP)
