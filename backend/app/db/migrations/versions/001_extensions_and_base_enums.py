"""001_extensions_and_base_enums

Revision ID: 001_extensions_and_base_enums
Revises:
Create Date: 2026-03-04 17:30:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_extensions_and_base_enums"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _enum(name: str, *values: str) -> sa.Enum:
    return sa.Enum(*values, name=name)


def upgrade() -> None:
    bind = op.get_bind()
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    _enum(
        "enquiry_status_enum",
        "RECEIVED",
        "IN_REVIEW",
        "QUOTED",
        "PENDING_APPROVAL",
        "APPROVED",
        "REJECTED",
        "PO_CREATED",
        "INVOICED",
        "IN_DELIVERY",
        "DELIVERED",
        "CLOSED",
        "CANCELLED",
    ).create(bind, checkfirst=True)

    _enum(
        "quotation_status_enum",
        "DRAFT",
        "PENDING_APPROVAL",
        "APPROVED",
        "REJECTED",
    ).create(bind, checkfirst=True)

    _enum(
        "approval_decision_enum",
        "PENDING",
        "APPROVED",
        "REJECTED",
    ).create(bind, checkfirst=True)

    _enum(
        "po_status_enum",
        "DRAFT",
        "ISSUED",
        "CONFIRMED",
        "CLOSED",
        "CANCELLED",
    ).create(bind, checkfirst=True)

    _enum(
        "invoice_status_enum",
        "UNPAID",
        "PARTIAL",
        "PAID",
        "VOID",
    ).create(bind, checkfirst=True)

    _enum(
        "delivery_status_enum",
        "PENDING",
        "IN_TRANSIT",
        "DELIVERED",
        "FAILED",
        "CANCELLED",
    ).create(bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()

    _enum(
        "delivery_status_enum",
        "PENDING",
        "IN_TRANSIT",
        "DELIVERED",
        "FAILED",
        "CANCELLED",
    ).drop(bind, checkfirst=True)

    _enum(
        "invoice_status_enum",
        "UNPAID",
        "PARTIAL",
        "PAID",
        "VOID",
    ).drop(bind, checkfirst=True)

    _enum(
        "po_status_enum",
        "DRAFT",
        "ISSUED",
        "CONFIRMED",
        "CLOSED",
        "CANCELLED",
    ).drop(bind, checkfirst=True)

    _enum(
        "approval_decision_enum",
        "PENDING",
        "APPROVED",
        "REJECTED",
    ).drop(bind, checkfirst=True)

    _enum(
        "quotation_status_enum",
        "DRAFT",
        "PENDING_APPROVAL",
        "APPROVED",
        "REJECTED",
    ).drop(bind, checkfirst=True)

    _enum(
        "enquiry_status_enum",
        "RECEIVED",
        "IN_REVIEW",
        "QUOTED",
        "PENDING_APPROVAL",
        "APPROVED",
        "REJECTED",
        "PO_CREATED",
        "INVOICED",
        "IN_DELIVERY",
        "DELIVERED",
        "CLOSED",
        "CANCELLED",
    ).drop(bind, checkfirst=True)

    op.execute('DROP EXTENSION IF EXISTS "pgcrypto";')
