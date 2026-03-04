from __future__ import annotations

import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.request_context import get_request_id
from app.core.security import now_utc
from app.models.audit_event import AuditEvent
from app.models.customer import Customer
from app.models.manufacturer import Manufacturer
from app.models.product import Product
from app.models.user import User
from app.schemas.masters import (
    CustomerCreate,
    CustomerUpdate,
    ImportErrorRow,
    ImportSummary,
    ManufacturerCreate,
    ManufacturerUpdate,
    ProductCreate,
    ProductUpdate,
)
from app.utils.excel import (
    ensure_template_columns,
    load_excel_dataframe,
    normalize_string,
    parse_bool,
)

CUSTOMER_REQUIRED_COLUMNS = {"code", "name", "country"}
CUSTOMER_ALLOWED_COLUMNS = {
    "code",
    "name",
    "country",
    "contact_name",
    "contact_email",
    "contact_phone",
    "is_active",
}

MANUFACTURER_REQUIRED_COLUMNS = {"code", "name", "country"}
MANUFACTURER_ALLOWED_COLUMNS = {"code", "name", "country", "is_active"}

PRODUCT_REQUIRED_COLUMNS = {"sku", "name", "manufacturer_code"}
PRODUCT_ALLOWED_COLUMNS = {"sku", "name", "manufacturer_code", "unit", "is_active"}


class MasterDataService:
    def __init__(self, db: Session):
        self.db = db

    # -----------------------------
    # Customers
    # -----------------------------
    def list_customers(self, *, offset: int = 0, limit: int = 100) -> list[Customer]:
        return list(
            self.db.scalars(
                select(Customer).order_by(Customer.created_at.desc()).offset(offset).limit(limit)
            )
        )

    def get_customer(self, customer_id: uuid.UUID) -> Customer:
        customer = self.db.get(Customer, customer_id)
        if customer is None:
            raise self._not_found("customer")
        return customer

    def create_customer(self, payload: CustomerCreate, actor_user: User) -> Customer:
        customer = Customer(
            code=payload.code.strip().upper(),
            name=payload.name.strip(),
            country=payload.country.strip(),
            contact_fields=payload.contact_fields,
            is_active=payload.is_active,
        )
        self.db.add(customer)
        self.db.flush()
        self._add_audit_event(
            actor_user=actor_user,
            entity_type="customer",
            entity_id=customer.id,
            action="CREATE",
            before_jsonb={},
            after_jsonb=self._customer_snapshot(customer),
        )
        return self._commit_and_refresh(customer)

    def update_customer(
        self,
        customer_id: uuid.UUID,
        payload: CustomerUpdate,
        actor_user: User,
    ) -> Customer:
        customer = self.get_customer(customer_id)
        before_snapshot = self._customer_snapshot(customer)
        data = payload.model_dump(exclude_unset=True)

        if "name" in data and data["name"] is not None:
            customer.name = data["name"].strip()
        if "country" in data and data["country"] is not None:
            customer.country = data["country"].strip()
        if "contact_fields" in data and data["contact_fields"] is not None:
            customer.contact_fields = data["contact_fields"]
        if "is_active" in data and data["is_active"] is not None:
            customer.is_active = data["is_active"]

        customer.updated_at = now_utc()
        self._add_audit_event(
            actor_user=actor_user,
            entity_type="customer",
            entity_id=customer.id,
            action="UPDATE",
            before_jsonb=before_snapshot,
            after_jsonb=self._customer_snapshot(customer),
        )
        return self._commit_and_refresh(customer)

    def delete_customer(self, customer_id: uuid.UUID, actor_user: User) -> None:
        customer = self.get_customer(customer_id)
        before_snapshot = self._customer_snapshot(customer)
        self._add_audit_event(
            actor_user=actor_user,
            entity_type="customer",
            entity_id=customer.id,
            action="DELETE",
            before_jsonb=before_snapshot,
            after_jsonb={},
        )
        self.db.delete(customer)
        self._commit()

    # -----------------------------
    # Manufacturers
    # -----------------------------
    def list_manufacturers(self, *, offset: int = 0, limit: int = 100) -> list[Manufacturer]:
        return list(
            self.db.scalars(
                select(Manufacturer)
                .order_by(Manufacturer.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
        )

    def get_manufacturer(self, manufacturer_id: uuid.UUID) -> Manufacturer:
        manufacturer = self.db.get(Manufacturer, manufacturer_id)
        if manufacturer is None:
            raise self._not_found("manufacturer")
        return manufacturer

    def create_manufacturer(self, payload: ManufacturerCreate, actor_user: User) -> Manufacturer:
        manufacturer = Manufacturer(
            code=payload.code.strip().upper(),
            name=payload.name.strip(),
            country=payload.country.strip(),
            is_active=payload.is_active,
        )
        self.db.add(manufacturer)
        self.db.flush()
        self._add_audit_event(
            actor_user=actor_user,
            entity_type="manufacturer",
            entity_id=manufacturer.id,
            action="CREATE",
            before_jsonb={},
            after_jsonb=self._manufacturer_snapshot(manufacturer),
        )
        return self._commit_and_refresh(manufacturer)

    def update_manufacturer(
        self,
        manufacturer_id: uuid.UUID,
        payload: ManufacturerUpdate,
        actor_user: User,
    ) -> Manufacturer:
        manufacturer = self.get_manufacturer(manufacturer_id)
        before_snapshot = self._manufacturer_snapshot(manufacturer)
        data = payload.model_dump(exclude_unset=True)

        if "name" in data and data["name"] is not None:
            manufacturer.name = data["name"].strip()
        if "country" in data and data["country"] is not None:
            manufacturer.country = data["country"].strip()
        if "is_active" in data and data["is_active"] is not None:
            manufacturer.is_active = data["is_active"]

        manufacturer.updated_at = now_utc()
        self._add_audit_event(
            actor_user=actor_user,
            entity_type="manufacturer",
            entity_id=manufacturer.id,
            action="UPDATE",
            before_jsonb=before_snapshot,
            after_jsonb=self._manufacturer_snapshot(manufacturer),
        )
        return self._commit_and_refresh(manufacturer)

    def delete_manufacturer(self, manufacturer_id: uuid.UUID, actor_user: User) -> None:
        manufacturer = self.get_manufacturer(manufacturer_id)
        before_snapshot = self._manufacturer_snapshot(manufacturer)
        self._add_audit_event(
            actor_user=actor_user,
            entity_type="manufacturer",
            entity_id=manufacturer.id,
            action="DELETE",
            before_jsonb=before_snapshot,
            after_jsonb={},
        )
        self.db.delete(manufacturer)
        self._commit()

    # -----------------------------
    # Products
    # -----------------------------
    def list_products(self, *, offset: int = 0, limit: int = 100) -> list[Product]:
        return list(
            self.db.scalars(
                select(Product)
                .options(selectinload(Product.manufacturer))
                .order_by(Product.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
        )

    def get_product(self, product_id: uuid.UUID) -> Product:
        product = self.db.scalar(
            select(Product)
            .options(selectinload(Product.manufacturer))
            .where(Product.id == product_id)
        )
        if product is None:
            raise self._not_found("product")
        return product

    def create_product(self, payload: ProductCreate, actor_user: User) -> Product:
        self._assert_manufacturer_exists(payload.manufacturer_id)

        product = Product(
            sku=payload.sku.strip().upper(),
            name=payload.name.strip(),
            manufacturer_id=payload.manufacturer_id,
            unit=payload.unit.strip(),
            is_active=payload.is_active,
        )
        self.db.add(product)
        self.db.flush()
        self._add_audit_event(
            actor_user=actor_user,
            entity_type="product",
            entity_id=product.id,
            action="CREATE",
            before_jsonb={},
            after_jsonb=self._product_snapshot(product),
        )
        return self._commit_and_refresh(product)

    def update_product(
        self,
        product_id: uuid.UUID,
        payload: ProductUpdate,
        actor_user: User,
    ) -> Product:
        product = self.get_product(product_id)
        before_snapshot = self._product_snapshot(product)
        data = payload.model_dump(exclude_unset=True)

        if "name" in data and data["name"] is not None:
            product.name = data["name"].strip()
        if "manufacturer_id" in data and data["manufacturer_id"] is not None:
            self._assert_manufacturer_exists(data["manufacturer_id"])
            product.manufacturer_id = data["manufacturer_id"]
        if "unit" in data and data["unit"] is not None:
            product.unit = data["unit"].strip()
        if "is_active" in data and data["is_active"] is not None:
            product.is_active = data["is_active"]

        product.updated_at = now_utc()
        self._add_audit_event(
            actor_user=actor_user,
            entity_type="product",
            entity_id=product.id,
            action="UPDATE",
            before_jsonb=before_snapshot,
            after_jsonb=self._product_snapshot(product),
        )
        return self._commit_and_refresh(product)

    def delete_product(self, product_id: uuid.UUID, actor_user: User) -> None:
        product = self.get_product(product_id)
        before_snapshot = self._product_snapshot(product)
        self._add_audit_event(
            actor_user=actor_user,
            entity_type="product",
            entity_id=product.id,
            action="DELETE",
            before_jsonb=before_snapshot,
            after_jsonb={},
        )
        self.db.delete(product)
        self._commit()

    # -----------------------------
    # Imports
    # -----------------------------
    def import_customers(self, file_bytes: bytes, actor_user: User) -> ImportSummary:
        df = load_excel_dataframe(file_bytes)
        ensure_template_columns(
            df,
            required_columns=CUSTOMER_REQUIRED_COLUMNS,
            allowed_columns=CUSTOMER_ALLOWED_COLUMNS,
        )
        rows = df.to_dict(orient="records")

        errors: list[ImportErrorRow] = []
        created_count = 0
        updated_count = 0

        for index, row in enumerate(rows, start=2):
            try:
                code = normalize_string(row.get("code")).upper()
                name = normalize_string(row.get("name"))
                country = normalize_string(row.get("country"))
                if not code or not name or not country:
                    raise ValueError("code, name and country are required")

                contact_fields: dict[str, Any] = {}
                for key in ("contact_name", "contact_email", "contact_phone"):
                    value = normalize_string(row.get(key))
                    if value:
                        contact_fields[key] = value

                is_active = parse_bool(row.get("is_active"), default=True)
                existing = self.db.scalar(select(Customer).where(Customer.code == code))

                if existing is None:
                    self.db.add(
                        Customer(
                            code=code,
                            name=name,
                            country=country,
                            contact_fields=contact_fields,
                            is_active=is_active,
                        )
                    )
                    created_count += 1
                else:
                    existing.name = name
                    existing.country = country
                    existing.contact_fields = contact_fields
                    existing.is_active = is_active
                    existing.updated_at = now_utc()
                    updated_count += 1

                self._commit()
            except (ValueError, IntegrityError) as exc:
                self.db.rollback()
                errors.append(
                    ImportErrorRow(
                        row_number=index,
                        error=str(exc),
                        payload={k: self._repr_value(v) for k, v in row.items()},
                    )
                )

        summary = ImportSummary(
            entity="customers",
            total_rows=len(rows),
            created_count=created_count,
            updated_count=updated_count,
            error_count=len(errors),
            errors=errors,
        )
        self._add_audit_event(
            actor_user=actor_user,
            entity_type="import_customers",
            entity_id=uuid.uuid4(),
            action="IMPORT",
            before_jsonb={},
            after_jsonb={
                "total_rows": summary.total_rows,
                "created_count": summary.created_count,
                "updated_count": summary.updated_count,
                "error_count": summary.error_count,
            },
        )
        self._commit()
        return summary

    def import_manufacturers(self, file_bytes: bytes, actor_user: User) -> ImportSummary:
        df = load_excel_dataframe(file_bytes)
        ensure_template_columns(
            df,
            required_columns=MANUFACTURER_REQUIRED_COLUMNS,
            allowed_columns=MANUFACTURER_ALLOWED_COLUMNS,
        )
        rows = df.to_dict(orient="records")

        errors: list[ImportErrorRow] = []
        created_count = 0
        updated_count = 0

        for index, row in enumerate(rows, start=2):
            try:
                code = normalize_string(row.get("code")).upper()
                name = normalize_string(row.get("name"))
                country = normalize_string(row.get("country"))
                if not code or not name or not country:
                    raise ValueError("code, name and country are required")

                is_active = parse_bool(row.get("is_active"), default=True)
                existing = self.db.scalar(select(Manufacturer).where(Manufacturer.code == code))

                if existing is None:
                    self.db.add(
                        Manufacturer(
                            code=code,
                            name=name,
                            country=country,
                            is_active=is_active,
                        )
                    )
                    created_count += 1
                else:
                    existing.name = name
                    existing.country = country
                    existing.is_active = is_active
                    existing.updated_at = now_utc()
                    updated_count += 1

                self._commit()
            except (ValueError, IntegrityError) as exc:
                self.db.rollback()
                errors.append(
                    ImportErrorRow(
                        row_number=index,
                        error=str(exc),
                        payload={k: self._repr_value(v) for k, v in row.items()},
                    )
                )

        summary = ImportSummary(
            entity="manufacturers",
            total_rows=len(rows),
            created_count=created_count,
            updated_count=updated_count,
            error_count=len(errors),
            errors=errors,
        )
        self._add_audit_event(
            actor_user=actor_user,
            entity_type="import_manufacturers",
            entity_id=uuid.uuid4(),
            action="IMPORT",
            before_jsonb={},
            after_jsonb={
                "total_rows": summary.total_rows,
                "created_count": summary.created_count,
                "updated_count": summary.updated_count,
                "error_count": summary.error_count,
            },
        )
        self._commit()
        return summary

    def import_products(self, file_bytes: bytes, actor_user: User) -> ImportSummary:
        df = load_excel_dataframe(file_bytes)
        ensure_template_columns(
            df,
            required_columns=PRODUCT_REQUIRED_COLUMNS,
            allowed_columns=PRODUCT_ALLOWED_COLUMNS,
        )
        rows = df.to_dict(orient="records")

        errors: list[ImportErrorRow] = []
        created_count = 0
        updated_count = 0

        for index, row in enumerate(rows, start=2):
            try:
                sku = normalize_string(row.get("sku")).upper()
                name = normalize_string(row.get("name"))
                manufacturer_code = normalize_string(row.get("manufacturer_code")).upper()
                if not sku or not name or not manufacturer_code:
                    raise ValueError("sku, name and manufacturer_code are required")

                manufacturer = self.db.scalar(
                    select(Manufacturer).where(Manufacturer.code == manufacturer_code)
                )
                if manufacturer is None:
                    raise ValueError(f"manufacturer not found for code '{manufacturer_code}'")

                unit = normalize_string(row.get("unit")) or "EA"
                is_active = parse_bool(row.get("is_active"), default=True)
                existing = self.db.scalar(select(Product).where(Product.sku == sku))

                if existing is None:
                    self.db.add(
                        Product(
                            sku=sku,
                            name=name,
                            manufacturer_id=manufacturer.id,
                            unit=unit,
                            is_active=is_active,
                        )
                    )
                    created_count += 1
                else:
                    existing.name = name
                    existing.manufacturer_id = manufacturer.id
                    existing.unit = unit
                    existing.is_active = is_active
                    existing.updated_at = now_utc()
                    updated_count += 1

                self._commit()
            except (ValueError, IntegrityError) as exc:
                self.db.rollback()
                errors.append(
                    ImportErrorRow(
                        row_number=index,
                        error=str(exc),
                        payload={k: self._repr_value(v) for k, v in row.items()},
                    )
                )

        summary = ImportSummary(
            entity="products",
            total_rows=len(rows),
            created_count=created_count,
            updated_count=updated_count,
            error_count=len(errors),
            errors=errors,
        )
        self._add_audit_event(
            actor_user=actor_user,
            entity_type="import_products",
            entity_id=uuid.uuid4(),
            action="IMPORT",
            before_jsonb={},
            after_jsonb={
                "total_rows": summary.total_rows,
                "created_count": summary.created_count,
                "updated_count": summary.updated_count,
                "error_count": summary.error_count,
            },
        )
        self._commit()
        return summary

    # -----------------------------
    # Internal helpers
    # -----------------------------
    def _assert_manufacturer_exists(self, manufacturer_id: uuid.UUID) -> None:
        if self.db.get(Manufacturer, manufacturer_id) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="manufacturer_id does not exist",
            )

    @staticmethod
    def _not_found(entity: str) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity} not found",
        )

    @staticmethod
    def _repr_value(value: Any) -> Any:
        if value is None:
            return None
        return str(value)

    @staticmethod
    def _customer_snapshot(customer: Customer) -> dict[str, Any]:
        return {
            "id": str(customer.id),
            "code": customer.code,
            "name": customer.name,
            "country": customer.country,
            "contact_fields": customer.contact_fields,
            "is_active": customer.is_active,
        }

    @staticmethod
    def _manufacturer_snapshot(manufacturer: Manufacturer) -> dict[str, Any]:
        return {
            "id": str(manufacturer.id),
            "code": manufacturer.code,
            "name": manufacturer.name,
            "country": manufacturer.country,
            "is_active": manufacturer.is_active,
        }

    @staticmethod
    def _product_snapshot(product: Product) -> dict[str, Any]:
        return {
            "id": str(product.id),
            "sku": product.sku,
            "name": product.name,
            "manufacturer_id": str(product.manufacturer_id),
            "unit": product.unit,
            "is_active": product.is_active,
        }

    def _add_audit_event(
        self,
        *,
        actor_user: User | None,
        entity_type: str,
        entity_id: uuid.UUID,
        action: str,
        before_jsonb: dict[str, Any],
        after_jsonb: dict[str, Any],
    ) -> None:
        self.db.add(
            AuditEvent(
                actor_user_id=actor_user.id if actor_user is not None else None,
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                before_jsonb=before_jsonb,
                after_jsonb=after_jsonb,
                request_id=get_request_id(),
            )
        )

    def _commit_and_refresh(self, instance: Any) -> Any:
        try:
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc.orig),
            ) from exc

    def _commit(self) -> None:
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc.orig),
            ) from exc
