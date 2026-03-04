from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rbac import Roles, require_roles
from app.db.session import get_db
from app.models.commercial import RTMPO, CustomerPO, Delivery, DeliveryEvent, Invoice, Payment
from app.models.user import User
from app.schemas.commercial import (
    CustomerPOCreateRequest,
    CustomerPORead,
    DeliveryCreateRequest,
    DeliveryEventCreateRequest,
    DeliveryEventRead,
    DeliveryRead,
    InvoiceCreateRequest,
    InvoiceRead,
    PaymentCreateRequest,
    PaymentRead,
    RTMPOCreateRequest,
    RTMPORead,
)
from app.services.commercial_service import CommercialService

router = APIRouter(tags=["commercial"])

COMMERCIAL_READ_ACCESS = Depends(
    require_roles(Roles.BD, Roles.ADMIN, Roles.SUPER_ADMIN, Roles.SUPPLY_CHAIN)
)
CUSTOMER_PO_ACCESS = Depends(require_roles(Roles.BD, Roles.ADMIN, Roles.SUPER_ADMIN))
RTM_PO_ACCESS = Depends(require_roles(Roles.SUPPLY_CHAIN, Roles.ADMIN, Roles.SUPER_ADMIN))
INVOICE_PAYMENT_ACCESS = Depends(require_roles(Roles.ADMIN, Roles.SUPER_ADMIN))
DELIVERY_WRITE_ACCESS = Depends(require_roles(Roles.SUPPLY_CHAIN, Roles.ADMIN, Roles.SUPER_ADMIN))


def get_commercial_service(db: Session = Depends(get_db)) -> CommercialService:
    return CommercialService(db=db, settings=get_settings())


@router.post(
    "/quotations/{quotation_id}/revisions/{revision_id}/customer-po",
    response_model=CustomerPORead,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_po(
    quotation_id: uuid.UUID,
    revision_id: uuid.UUID,
    payload: CustomerPOCreateRequest,
    current_user: User = CUSTOMER_PO_ACCESS,
    service: CommercialService = Depends(get_commercial_service),
) -> CustomerPO:
    return service.create_customer_po(quotation_id, revision_id, payload, current_user)


@router.post(
    "/quotations/{quotation_id}/revisions/{revision_id}/rtm-po",
    response_model=RTMPORead,
    status_code=status.HTTP_201_CREATED,
)
def create_rtm_po(
    quotation_id: uuid.UUID,
    revision_id: uuid.UUID,
    payload: RTMPOCreateRequest,
    current_user: User = RTM_PO_ACCESS,
    service: CommercialService = Depends(get_commercial_service),
) -> RTMPO:
    return service.create_rtm_po(quotation_id, revision_id, payload, current_user)


@router.post(
    "/invoices",
    response_model=InvoiceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice(
    payload: InvoiceCreateRequest,
    current_user: User = INVOICE_PAYMENT_ACCESS,
    service: CommercialService = Depends(get_commercial_service),
) -> Invoice:
    return service.create_invoice(payload, current_user)


@router.post(
    "/payments",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    payload: PaymentCreateRequest,
    current_user: User = INVOICE_PAYMENT_ACCESS,
    service: CommercialService = Depends(get_commercial_service),
) -> Payment:
    return service.create_payment(payload, current_user)


@router.post(
    "/deliveries",
    response_model=DeliveryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_delivery(
    payload: DeliveryCreateRequest,
    current_user: User = DELIVERY_WRITE_ACCESS,
    service: CommercialService = Depends(get_commercial_service),
) -> Delivery:
    return service.create_delivery(payload, current_user)


@router.post(
    "/deliveries/{delivery_id}/events",
    response_model=DeliveryEventRead,
    status_code=status.HTTP_201_CREATED,
)
def add_delivery_event(
    delivery_id: uuid.UUID,
    payload: DeliveryEventCreateRequest,
    current_user: User = DELIVERY_WRITE_ACCESS,
    service: CommercialService = Depends(get_commercial_service),
) -> DeliveryEvent:
    return service.add_delivery_event(delivery_id, payload, current_user)


@router.get("/deliveries/{delivery_id}", response_model=DeliveryRead)
def get_delivery(
    delivery_id: uuid.UUID,
    _: User = COMMERCIAL_READ_ACCESS,
    service: CommercialService = Depends(get_commercial_service),
) -> Delivery:
    return service.get_delivery(delivery_id)
