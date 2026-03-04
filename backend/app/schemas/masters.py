from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CustomerBase(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    country: str = Field(min_length=1, max_length=120)
    contact_fields: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    country: str | None = Field(default=None, min_length=1, max_length=120)
    contact_fields: dict[str, Any] | None = None
    is_active: bool | None = None


class CustomerRead(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ManufacturerBase(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    country: str = Field(min_length=1, max_length=120)
    is_active: bool = True


class ManufacturerCreate(ManufacturerBase):
    pass


class ManufacturerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    country: str | None = Field(default=None, min_length=1, max_length=120)
    is_active: bool | None = None


class ManufacturerRead(ManufacturerBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ProductBase(BaseModel):
    sku: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=255)
    manufacturer_id: uuid.UUID
    unit: str = Field(default="EA", min_length=1, max_length=50)
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    manufacturer_id: uuid.UUID | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=50)
    is_active: bool | None = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ProductImportRow(BaseModel):
    sku: str
    name: str
    manufacturer_code: str
    unit: str = "EA"
    is_active: bool = True


class ImportErrorRow(BaseModel):
    row_number: int
    error: str
    payload: dict[str, Any]


class ImportSummary(BaseModel):
    entity: str
    total_rows: int
    created_count: int
    updated_count: int
    error_count: int
    errors: list[ImportErrorRow]
