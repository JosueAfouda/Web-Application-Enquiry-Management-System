"""005_quote_approval_workflow

Revision ID: 005_quote_approval_workflow
Revises: 004_enquiries_workflow
Create Date: 2026-03-04 18:40:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "005_quote_approval_workflow"
down_revision: str | None = "004_enquiries_workflow"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    quotation_status_enum = postgresql.ENUM(name="quotation_status_enum", create_type=False)
    approval_decision_enum = postgresql.ENUM(name="approval_decision_enum", create_type=False)

    op.create_table(
        "quotations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "enquiry_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("enquiries.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("quotation_no", sa.String(length=80), nullable=False),
        sa.Column(
            "current_revision_no",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "status",
            quotation_status_enum,
            nullable=False,
            server_default=sa.text("'DRAFT'"),
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
        sa.UniqueConstraint("quotation_no", name="uq_quotations_quotation_no"),
        sa.CheckConstraint(
            "current_revision_no >= 0",
            name="ck_quotations_current_revision_no_nonneg",
        ),
    )
    op.create_index("ix_quotations_enquiry_id", "quotations", ["enquiry_id"], unique=False)
    op.create_index("ix_quotations_status", "quotations", ["status"], unique=False)

    op.create_table(
        "quotation_revisions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "quotation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("quotations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("revision_no", sa.Integer(), nullable=False),
        sa.Column(
            "freight",
            sa.Numeric(14, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "markup_percent",
            sa.Numeric(6, 3),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "subtotal",
            sa.Numeric(14, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "total",
            sa.Numeric(14, 2),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
            server_default=sa.text("'USD'"),
        ),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "quotation_id",
            "revision_no",
            name="uq_quotation_revisions_quotation_id_revision_no",
        ),
        sa.CheckConstraint("revision_no > 0", name="ck_quotation_revisions_revision_no_pos"),
        sa.CheckConstraint("freight >= 0", name="ck_quotation_revisions_freight_nonneg"),
        sa.CheckConstraint(
            "markup_percent >= 0",
            name="ck_quotation_revisions_markup_percent_nonneg",
        ),
        sa.CheckConstraint("subtotal >= 0", name="ck_quotation_revisions_subtotal_nonneg"),
        sa.CheckConstraint("total >= 0", name="ck_quotation_revisions_total_nonneg"),
    )
    op.create_index(
        "ix_quotation_revisions_quotation_id",
        "quotation_revisions",
        ["quotation_id"],
        unique=False,
    )

    op.create_table(
        "quotation_items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "revision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("quotation_revisions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "enquiry_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("enquiry_items.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("qty", sa.Numeric(14, 3), nullable=False),
        sa.Column("unit_price", sa.Numeric(14, 4), nullable=False),
        sa.Column("line_total", sa.Numeric(14, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("qty >= 0", name="ck_quotation_items_qty_nonneg"),
        sa.CheckConstraint(
            "unit_price >= 0",
            name="ck_quotation_items_unit_price_nonneg",
        ),
        sa.CheckConstraint(
            "line_total >= 0",
            name="ck_quotation_items_line_total_nonneg",
        ),
    )
    op.create_index(
        "ix_quotation_items_revision_id",
        "quotation_items",
        ["revision_id"],
        unique=False,
    )

    op.create_table(
        "approvals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "revision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("quotation_revisions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "step_name",
            sa.String(length=80),
            nullable=False,
            server_default=sa.text("'FINAL'"),
        ),
        sa.Column(
            "decision",
            approval_decision_enum,
            nullable=False,
            server_default=sa.text("'PENDING'"),
        ),
        sa.Column(
            "decided_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("revision_id", "step_name", name="uq_approvals_revision_id_step_name"),
    )
    op.create_index("ix_approvals_revision_id", "approvals", ["revision_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_approvals_revision_id", table_name="approvals")
    op.drop_table("approvals")

    op.drop_index("ix_quotation_items_revision_id", table_name="quotation_items")
    op.drop_table("quotation_items")

    op.drop_index("ix_quotation_revisions_quotation_id", table_name="quotation_revisions")
    op.drop_table("quotation_revisions")

    op.drop_index("ix_quotations_status", table_name="quotations")
    op.drop_index("ix_quotations_enquiry_id", table_name="quotations")
    op.drop_table("quotations")
