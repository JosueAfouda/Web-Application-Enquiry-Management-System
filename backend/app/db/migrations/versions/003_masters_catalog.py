"""003_masters_catalog

Revision ID: 003_masters_catalog
Revises: 002_roles_users_sessions
Create Date: 2026-03-04 18:05:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003_masters_catalog"
down_revision: str | None = "002_roles_users_sessions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("country", sa.String(length=120), nullable=False),
        sa.Column(
            "contact_fields",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_customers_code"),
    )

    op.create_table(
        "manufacturers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("country", sa.String(length=120), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_manufacturers_code"),
    )

    op.create_table(
        "products",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("sku", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "manufacturer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("manufacturers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "unit",
            sa.String(length=50),
            nullable=False,
            server_default=sa.text("'EA'"),
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sku", name="uq_products_sku"),
    )

    op.create_index("ix_products_manufacturer_id", "products", ["manufacturer_id"], unique=False)
    op.create_index(
        "uq_customers_name_country_ci",
        "customers",
        [sa.text("lower(name)"), sa.text("lower(country)")],
        unique=True,
    )
    op.create_index(
        "uq_manufacturers_name_country_ci",
        "manufacturers",
        [sa.text("lower(name)"), sa.text("lower(country)")],
        unique=True,
    )
    op.create_index(
        "uq_products_name_manufacturer_ci",
        "products",
        [sa.text("lower(name)"), "manufacturer_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_products_name_manufacturer_ci", table_name="products")
    op.drop_index("uq_manufacturers_name_country_ci", table_name="manufacturers")
    op.drop_index("uq_customers_name_country_ci", table_name="customers")
    op.drop_index("ix_products_manufacturer_id", table_name="products")

    op.drop_table("products")
    op.drop_table("manufacturers")
    op.drop_table("customers")
