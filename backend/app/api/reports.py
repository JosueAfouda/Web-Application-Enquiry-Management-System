from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.rbac import Roles, require_roles
from app.db.session import get_db
from app.models.user import User
from app.schemas.reports import KPIReportRead
from app.services.reports_service import ReportsService

router = APIRouter(prefix="/reports", tags=["reports"])
REPORT_ACCESS = Depends(require_roles(Roles.ADMIN, Roles.SUPER_ADMIN))


def get_reports_service(db: Session = Depends(get_db)) -> ReportsService:
    return ReportsService(db=db)


@router.get("/kpis", response_model=KPIReportRead)
def get_kpis(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    _: User = REPORT_ACCESS,
    service: ReportsService = Depends(get_reports_service),
) -> KPIReportRead:
    return service.get_kpis(date_from=date_from, date_to=date_to)


@router.get("/enquiries.xlsx")
def export_enquiries(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    status: str | None = Query(default=None),
    _: User = REPORT_ACCESS,
    service: ReportsService = Depends(get_reports_service),
) -> Response:
    payload = service.export_enquiries(date_from=date_from, date_to=date_to, status=status)
    return Response(
        content=payload,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={"Content-Disposition": 'attachment; filename="enquiries.xlsx"'},
    )


@router.get("/quotations.xlsx")
def export_quotations(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    status: str | None = Query(default=None),
    _: User = REPORT_ACCESS,
    service: ReportsService = Depends(get_reports_service),
) -> Response:
    payload = service.export_quotations(date_from=date_from, date_to=date_to, status=status)
    return Response(
        content=payload,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={"Content-Disposition": 'attachment; filename="quotations.xlsx"'},
    )


@router.get("/invoices.xlsx")
def export_invoices(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    status: str | None = Query(default=None),
    _: User = REPORT_ACCESS,
    service: ReportsService = Depends(get_reports_service),
) -> Response:
    payload = service.export_invoices(date_from=date_from, date_to=date_to, status=status)
    return Response(
        content=payload,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={"Content-Disposition": 'attachment; filename="invoices.xlsx"'},
    )


@router.get("/payments.xlsx")
def export_payments(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    method: str | None = Query(default=None),
    _: User = REPORT_ACCESS,
    service: ReportsService = Depends(get_reports_service),
) -> Response:
    payload = service.export_payments(date_from=date_from, date_to=date_to, method=method)
    return Response(
        content=payload,
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={"Content-Disposition": 'attachment; filename="payments.xlsx"'},
    )
