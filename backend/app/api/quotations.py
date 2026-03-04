from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.rbac import Roles, require_roles
from app.db.session import get_db
from app.models.quotation import Quotation, QuotationRevision
from app.models.user import User
from app.schemas.quotations import (
    QuotationActionRequest,
    QuotationApprovalActionRequest,
    QuotationCreateRequest,
    QuotationDetailRead,
    QuotationRead,
    QuotationRevisionCreateRequest,
    QuotationRevisionRead,
)
from app.services.quotations_service import QuotationService

router = APIRouter(tags=["quotations"])
QUOTE_READ_ACCESS = Depends(
    require_roles(Roles.BD, Roles.ADMIN, Roles.SUPER_ADMIN, Roles.SUPPLY_CHAIN)
)
QUOTE_WRITE_ACCESS = Depends(require_roles(Roles.BD, Roles.ADMIN, Roles.SUPER_ADMIN))
QUOTE_APPROVAL_ACCESS = Depends(require_roles(Roles.ADMIN, Roles.SUPER_ADMIN))


def get_quotation_service(db: Session = Depends(get_db)) -> QuotationService:
    return QuotationService(db=db)


@router.post(
    "/enquiries/{enquiry_id}/quotations",
    response_model=QuotationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_quotation(
    enquiry_id: uuid.UUID,
    payload: QuotationCreateRequest,
    current_user: User = Depends(require_roles(Roles.BD, Roles.ADMIN, Roles.SUPER_ADMIN)),
    service: QuotationService = Depends(get_quotation_service),
) -> Quotation:
    return service.create_quotation(enquiry_id, payload, current_user)


@router.post(
    "/quotations/{quotation_id}/revisions",
    response_model=QuotationRevisionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_revision(
    quotation_id: uuid.UUID,
    payload: QuotationRevisionCreateRequest,
    current_user: User = Depends(require_roles(Roles.BD, Roles.ADMIN, Roles.SUPER_ADMIN)),
    service: QuotationService = Depends(get_quotation_service),
) -> QuotationRevision:
    return service.create_revision(quotation_id, payload, current_user)


@router.get("/quotations/{quotation_id}", response_model=QuotationDetailRead)
def get_quotation(
    quotation_id: uuid.UUID,
    _: User = QUOTE_READ_ACCESS,
    service: QuotationService = Depends(get_quotation_service),
) -> Quotation:
    return service.get_quotation(quotation_id)


@router.get(
    "/quotations/{quotation_id}/revisions/{revision_id}",
    response_model=QuotationRevisionRead,
)
def get_revision(
    quotation_id: uuid.UUID,
    revision_id: uuid.UUID,
    _: User = QUOTE_READ_ACCESS,
    service: QuotationService = Depends(get_quotation_service),
) -> QuotationRevision:
    return service.get_revision(quotation_id, revision_id)


@router.post(
    "/quotations/{quotation_id}/revisions/{revision_id}/submit",
    response_model=QuotationRevisionRead,
)
def submit_revision(
    quotation_id: uuid.UUID,
    revision_id: uuid.UUID,
    payload: QuotationActionRequest,
    current_user: User = Depends(require_roles(Roles.BD, Roles.ADMIN, Roles.SUPER_ADMIN)),
    service: QuotationService = Depends(get_quotation_service),
) -> QuotationRevision:
    return service.submit_revision(quotation_id, revision_id, current_user, payload.remarks)


@router.post(
    "/quotations/{quotation_id}/revisions/{revision_id}/approve",
    response_model=QuotationRevisionRead,
)
def approve_revision(
    quotation_id: uuid.UUID,
    revision_id: uuid.UUID,
    payload: QuotationApprovalActionRequest,
    current_user: User = Depends(require_roles(Roles.ADMIN, Roles.SUPER_ADMIN)),
    service: QuotationService = Depends(get_quotation_service),
) -> QuotationRevision:
    return service.approve_revision(quotation_id, revision_id, current_user, payload.remarks)


@router.post(
    "/quotations/{quotation_id}/revisions/{revision_id}/reject",
    response_model=QuotationRevisionRead,
)
def reject_revision(
    quotation_id: uuid.UUID,
    revision_id: uuid.UUID,
    payload: QuotationApprovalActionRequest,
    current_user: User = Depends(require_roles(Roles.ADMIN, Roles.SUPER_ADMIN)),
    service: QuotationService = Depends(get_quotation_service),
) -> QuotationRevision:
    return service.reject_revision(quotation_id, revision_id, current_user, payload.remarks)
