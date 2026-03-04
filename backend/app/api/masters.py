from __future__ import annotations

import io
import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.rbac import Roles, require_roles
from app.db.session import get_db
from app.models.customer import Customer
from app.models.manufacturer import Manufacturer
from app.models.product import Product
from app.models.user import User
from app.schemas.masters import (
    CustomerCreate,
    CustomerRead,
    CustomerUpdate,
    ImportSummary,
    ManufacturerCreate,
    ManufacturerRead,
    ManufacturerUpdate,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from app.services.masters_service import MasterDataService
from app.utils.excel import build_error_report_csv

router = APIRouter(tags=["masters"])
MASTER_READ_ACCESS = Depends(
    require_roles(Roles.BD, Roles.ADMIN, Roles.SUPER_ADMIN, Roles.SUPPLY_CHAIN)
)
MASTER_WRITE_ACCESS = Depends(require_roles(Roles.ADMIN, Roles.SUPER_ADMIN))


def get_master_service(db: Session = Depends(get_db)) -> MasterDataService:
    return MasterDataService(db=db)


@router.get("/customers", response_model=list[CustomerRead])
def list_customers(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    _: object = MASTER_READ_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> list[Customer]:
    return service.list_customers(offset=offset, limit=limit)


@router.post("/customers", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(
    payload: CustomerCreate,
    current_user: User = MASTER_WRITE_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> Customer:
    return service.create_customer(payload, current_user)


@router.get("/customers/{customer_id}", response_model=CustomerRead)
def get_customer(
    customer_id: uuid.UUID,
    _: object = MASTER_READ_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> Customer:
    return service.get_customer(customer_id)


@router.put("/customers/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id: uuid.UUID,
    payload: CustomerUpdate,
    current_user: User = MASTER_WRITE_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> Customer:
    return service.update_customer(customer_id, payload, current_user)


@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: uuid.UUID,
    current_user: User = MASTER_WRITE_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> Response:
    service.delete_customer(customer_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/manufacturers", response_model=list[ManufacturerRead])
def list_manufacturers(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    _: object = MASTER_READ_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> list[Manufacturer]:
    return service.list_manufacturers(offset=offset, limit=limit)


@router.post(
    "/manufacturers",
    response_model=ManufacturerRead,
    status_code=status.HTTP_201_CREATED,
)
def create_manufacturer(
    payload: ManufacturerCreate,
    current_user: User = MASTER_WRITE_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> Manufacturer:
    return service.create_manufacturer(payload, current_user)


@router.get("/manufacturers/{manufacturer_id}", response_model=ManufacturerRead)
def get_manufacturer(
    manufacturer_id: uuid.UUID,
    _: object = MASTER_READ_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> Manufacturer:
    return service.get_manufacturer(manufacturer_id)


@router.put("/manufacturers/{manufacturer_id}", response_model=ManufacturerRead)
def update_manufacturer(
    manufacturer_id: uuid.UUID,
    payload: ManufacturerUpdate,
    current_user: User = MASTER_WRITE_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> Manufacturer:
    return service.update_manufacturer(manufacturer_id, payload, current_user)


@router.delete("/manufacturers/{manufacturer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_manufacturer(
    manufacturer_id: uuid.UUID,
    current_user: User = MASTER_WRITE_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> Response:
    service.delete_manufacturer(manufacturer_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/products", response_model=list[ProductRead])
def list_products(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    _: object = MASTER_READ_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> list[Product]:
    return service.list_products(offset=offset, limit=limit)


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    current_user: User = MASTER_WRITE_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> Product:
    return service.create_product(payload, current_user)


@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(
    product_id: uuid.UUID,
    _: object = MASTER_READ_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> Product:
    return service.get_product(product_id)


@router.put("/products/{product_id}", response_model=ProductRead)
def update_product(
    product_id: uuid.UUID,
    payload: ProductUpdate,
    current_user: User = MASTER_WRITE_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> Product:
    return service.update_product(product_id, payload, current_user)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: uuid.UUID,
    current_user: User = MASTER_WRITE_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> Response:
    service.delete_product(product_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/imports/customers",
    response_model=ImportSummary,
    responses={200: {"content": {"text/csv": {}}}},
)
async def import_customers(
    file: UploadFile = File(...),
    download_errors: bool = Query(default=False),
    current_user: User = MASTER_WRITE_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> Any:
    file_bytes = await file.read()
    summary = service.import_customers(file_bytes, current_user)

    if download_errors and summary.error_count > 0:
        csv_bytes = build_error_report_csv(summary.errors)
        return StreamingResponse(
            io.BytesIO(csv_bytes),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=customers_import_errors.csv"},
        )

    return summary


@router.post(
    "/imports/manufacturers",
    response_model=ImportSummary,
    responses={200: {"content": {"text/csv": {}}}},
)
async def import_manufacturers(
    file: UploadFile = File(...),
    download_errors: bool = Query(default=False),
    current_user: User = MASTER_WRITE_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> Any:
    file_bytes = await file.read()
    summary = service.import_manufacturers(file_bytes, current_user)

    if download_errors and summary.error_count > 0:
        csv_bytes = build_error_report_csv(summary.errors)
        return StreamingResponse(
            io.BytesIO(csv_bytes),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=manufacturers_import_errors.csv"},
        )

    return summary


@router.post(
    "/imports/products",
    response_model=ImportSummary,
    responses={200: {"content": {"text/csv": {}}}},
)
async def import_products(
    file: UploadFile = File(...),
    download_errors: bool = Query(default=False),
    current_user: User = MASTER_WRITE_ACCESS,
    service: MasterDataService = Depends(get_master_service),
) -> Any:
    file_bytes = await file.read()
    summary = service.import_products(file_bytes, current_user)

    if download_errors and summary.error_count > 0:
        csv_bytes = build_error_report_csv(summary.errors)
        return StreamingResponse(
            io.BytesIO(csv_bytes),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=products_import_errors.csv"},
        )

    return summary
