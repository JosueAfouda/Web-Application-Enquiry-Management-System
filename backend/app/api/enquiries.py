from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.rbac import Roles, require_roles
from app.db.session import get_db
from app.models.enquiry import Enquiry, EnquiryStatusHistory
from app.models.user import User
from app.schemas.enquiries import (
    EnquiryCreate,
    EnquiryRead,
    EnquiryStatus,
    EnquiryStatusHistoryRead,
    EnquiryStatusTransitionRequest,
)
from app.services.enquiries_service import EnquiryService

router = APIRouter(prefix="/enquiries", tags=["enquiries"])
ENQUIRY_READ_ACCESS = Depends(
    require_roles(Roles.BD, Roles.ADMIN, Roles.SUPER_ADMIN, Roles.SUPPLY_CHAIN)
)
ENQUIRY_CREATE_ACCESS = Depends(require_roles(Roles.BD, Roles.ADMIN, Roles.SUPER_ADMIN))
ENQUIRY_STATUS_ACCESS = Depends(
    require_roles(Roles.BD, Roles.ADMIN, Roles.SUPER_ADMIN, Roles.SUPPLY_CHAIN)
)


def get_enquiry_service(db: Session = Depends(get_db)) -> EnquiryService:
    return EnquiryService(db=db)


@router.post("", response_model=EnquiryRead, status_code=status.HTTP_201_CREATED)
def create_enquiry(
    payload: EnquiryCreate,
    current_user: User = Depends(require_roles(Roles.BD, Roles.ADMIN, Roles.SUPER_ADMIN)),
    service: EnquiryService = Depends(get_enquiry_service),
) -> Enquiry:
    return service.create_enquiry(payload, current_user)


@router.get("", response_model=list[EnquiryRead])
def list_enquiries(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    status: EnquiryStatus | None = Query(default=None),
    _: object = ENQUIRY_READ_ACCESS,
    service: EnquiryService = Depends(get_enquiry_service),
) -> list[Enquiry]:
    return service.list_enquiries(offset=offset, limit=limit, status_filter=status)


@router.get("/{enquiry_id}", response_model=EnquiryRead)
def get_enquiry(
    enquiry_id: uuid.UUID,
    _: object = ENQUIRY_READ_ACCESS,
    service: EnquiryService = Depends(get_enquiry_service),
) -> Enquiry:
    return service.get_enquiry(enquiry_id)


@router.post("/{enquiry_id}/status", response_model=EnquiryRead)
def transition_enquiry_status(
    enquiry_id: uuid.UUID,
    payload: EnquiryStatusTransitionRequest,
    current_user: User = Depends(
        require_roles(Roles.BD, Roles.ADMIN, Roles.SUPER_ADMIN, Roles.SUPPLY_CHAIN)
    ),
    service: EnquiryService = Depends(get_enquiry_service),
) -> Enquiry:
    return service.transition_status(enquiry_id, payload, current_user)


@router.get("/{enquiry_id}/history", response_model=list[EnquiryStatusHistoryRead])
def enquiry_history(
    enquiry_id: uuid.UUID,
    _: object = ENQUIRY_READ_ACCESS,
    service: EnquiryService = Depends(get_enquiry_service),
) -> list[EnquiryStatusHistory]:
    return service.history(enquiry_id)
