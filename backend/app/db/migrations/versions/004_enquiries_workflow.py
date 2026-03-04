"""004_enquiries_workflow

Revision ID: 004_enquiries_workflow
Revises: 003_masters_catalog
Create Date: 2026-03-04 18:20:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "004_enquiries_workflow"
down_revision: str | None = "003_masters_catalog"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    enquiry_status_enum = postgresql.ENUM(name="enquiry_status_enum", create_type=False)

    op.create_table(
        "enquiries",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("enquiry_no", sa.String(length=80), nullable=False),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "owner_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "status",
            enquiry_status_enum,
            nullable=False,
            server_default=sa.text("'RECEIVED'"),
        ),
        sa.Column(
            "received_date",
            sa.Date(),
            nullable=False,
            server_default=sa.text("CURRENT_DATE"),
        ),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default=sa.text("'USD'")),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.UniqueConstraint("enquiry_no", name="uq_enquiries_enquiry_no"),
    )
    op.create_index("ix_enquiries_customer_id", "enquiries", ["customer_id"], unique=False)
    op.create_index("ix_enquiries_owner_user_id", "enquiries", ["owner_user_id"], unique=False)
    op.create_index("ix_enquiries_status", "enquiries", ["status"], unique=False)
    op.create_index("ix_enquiries_received_date", "enquiries", ["received_date"], unique=False)

    op.create_table(
        "enquiry_items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "enquiry_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("enquiries.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("requested_qty", sa.Numeric(14, 3), nullable=False),
        sa.Column("target_price", sa.Numeric(14, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("requested_qty >= 0", name="ck_enquiry_items_requested_qty_nonneg"),
        sa.CheckConstraint(
            "target_price IS NULL OR target_price >= 0",
            name="ck_enquiry_items_target_price_nonneg",
        ),
    )
    op.create_index("ix_enquiry_items_enquiry_id", "enquiry_items", ["enquiry_id"], unique=False)

    op.create_table(
        "enquiry_status_history",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "enquiry_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("enquiries.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("from_status", enquiry_status_enum, nullable=True),
        sa.Column("to_status", enquiry_status_enum, nullable=False),
        sa.Column(
            "changed_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_enquiry_status_history_enquiry_id",
        "enquiry_status_history",
        ["enquiry_id"],
        unique=False,
    )

    op.create_table(
        "audit_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "actor_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column(
            "before_jsonb",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "after_jsonb",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("request_id", sa.String(length=120), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_audit_events_actor_user_id",
        "audit_events",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_audit_events_entity_type",
        "audit_events",
        ["entity_type"],
        unique=False,
    )
    op.create_index("ix_audit_events_entity_id", "audit_events", ["entity_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_events_entity_id", table_name="audit_events")
    op.drop_index("ix_audit_events_entity_type", table_name="audit_events")
    op.drop_index("ix_audit_events_actor_user_id", table_name="audit_events")
    op.drop_table("audit_events")

    op.drop_index("ix_enquiry_status_history_enquiry_id", table_name="enquiry_status_history")
    op.drop_table("enquiry_status_history")

    op.drop_index("ix_enquiry_items_enquiry_id", table_name="enquiry_items")
    op.drop_table("enquiry_items")

    op.drop_index("ix_enquiries_received_date", table_name="enquiries")
    op.drop_index("ix_enquiries_status", table_name="enquiries")
    op.drop_index("ix_enquiries_owner_user_id", table_name="enquiries")
    op.drop_index("ix_enquiries_customer_id", table_name="enquiries")
    op.drop_table("enquiries")
