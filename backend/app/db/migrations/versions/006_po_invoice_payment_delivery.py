"""006_po_invoice_payment_delivery

Revision ID: 006_po_invoice_payment_delivery
Revises: 005_quote_approval_workflow
Create Date: 2026-03-04 19:35:00

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "006_po_invoice_payment_delivery"
down_revision: str | None = "005_quote_approval_workflow"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    po_status_enum = postgresql.ENUM(name="po_status_enum", create_type=False)
    invoice_status_enum = postgresql.ENUM(name="invoice_status_enum", create_type=False)
    delivery_status_enum = postgresql.ENUM(name="delivery_status_enum", create_type=False)

    op.create_table(
        "customer_pos",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("po_no", sa.String(length=80), nullable=False),
        sa.Column(
            "enquiry_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("enquiries.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "quotation_revision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("quotation_revisions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "po_date",
            sa.Date(),
            nullable=False,
            server_default=sa.text("CURRENT_DATE"),
        ),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "status",
            po_status_enum,
            nullable=False,
            server_default=sa.text("'ISSUED'"),
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
        sa.UniqueConstraint("po_no", name="uq_customer_pos_po_no"),
        sa.CheckConstraint("total_amount >= 0", name="ck_customer_pos_total_amount_nonneg"),
    )
    op.create_index("ix_customer_pos_enquiry_id", "customer_pos", ["enquiry_id"], unique=False)
    op.create_index(
        "ix_customer_pos_quotation_revision_id",
        "customer_pos",
        ["quotation_revision_id"],
        unique=False,
    )
    op.create_index("ix_customer_pos_customer_id", "customer_pos", ["customer_id"], unique=False)
    op.create_index("ix_customer_pos_status", "customer_pos", ["status"], unique=False)

    op.create_table(
        "rtm_pos",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("po_no", sa.String(length=80), nullable=False),
        sa.Column(
            "enquiry_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("enquiries.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "quotation_revision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("quotation_revisions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "manufacturer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("manufacturers.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "po_date",
            sa.Date(),
            nullable=False,
            server_default=sa.text("CURRENT_DATE"),
        ),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "status",
            po_status_enum,
            nullable=False,
            server_default=sa.text("'ISSUED'"),
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
        sa.UniqueConstraint("po_no", name="uq_rtm_pos_po_no"),
        sa.CheckConstraint("total_amount >= 0", name="ck_rtm_pos_total_amount_nonneg"),
    )
    op.create_index("ix_rtm_pos_enquiry_id", "rtm_pos", ["enquiry_id"], unique=False)
    op.create_index(
        "ix_rtm_pos_quotation_revision_id",
        "rtm_pos",
        ["quotation_revision_id"],
        unique=False,
    )
    op.create_index("ix_rtm_pos_manufacturer_id", "rtm_pos", ["manufacturer_id"], unique=False)
    op.create_index("ix_rtm_pos_status", "rtm_pos", ["status"], unique=False)

    op.create_table(
        "invoices",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("invoice_no", sa.String(length=80), nullable=False),
        sa.Column(
            "enquiry_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("enquiries.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "customer_po_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customer_pos.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "issue_date",
            sa.Date(),
            nullable=False,
            server_default=sa.text("CURRENT_DATE"),
        ),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default=sa.text("'USD'")),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column(
            "status",
            invoice_status_enum,
            nullable=False,
            server_default=sa.text("'UNPAID'"),
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
        sa.UniqueConstraint("invoice_no", name="uq_invoices_invoice_no"),
        sa.CheckConstraint("total_amount >= 0", name="ck_invoices_total_amount_nonneg"),
        sa.CheckConstraint(
            "due_date IS NULL OR due_date >= issue_date",
            name="ck_invoices_due_not_before_issue",
        ),
    )
    op.create_index("ix_invoices_enquiry_id", "invoices", ["enquiry_id"], unique=False)
    op.create_index("ix_invoices_customer_po_id", "invoices", ["customer_po_id"], unique=False)
    op.create_index("ix_invoices_status", "invoices", ["status"], unique=False)

    op.create_table(
        "payments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "invoice_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("invoices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "payment_date",
            sa.Date(),
            nullable=False,
            server_default=sa.text("CURRENT_DATE"),
        ),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("method", sa.String(length=80), nullable=False),
        sa.Column("reference_no", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("amount > 0", name="ck_payments_amount_pos"),
    )
    op.create_index("ix_payments_invoice_id", "payments", ["invoice_id"], unique=False)

    op.create_table(
        "deliveries",
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
        sa.Column(
            "invoice_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("invoices.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("shipment_no", sa.String(length=80), nullable=True),
        sa.Column("courier_name", sa.String(length=120), nullable=True),
        sa.Column("tracking_no", sa.String(length=120), nullable=True),
        sa.Column("shipped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expected_delivery_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            delivery_status_enum,
            nullable=False,
            server_default=sa.text("'PENDING'"),
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
        sa.UniqueConstraint("shipment_no", name="uq_deliveries_shipment_no"),
        sa.CheckConstraint(
            "delivered_at IS NULL OR shipped_at IS NULL OR delivered_at >= shipped_at",
            name="ck_deliveries_delivered_after_shipped",
        ),
    )
    op.create_index("ix_deliveries_enquiry_id", "deliveries", ["enquiry_id"], unique=False)
    op.create_index("ix_deliveries_invoice_id", "deliveries", ["invoice_id"], unique=False)
    op.create_index("ix_deliveries_status", "deliveries", ["status"], unique=False)

    op.create_table(
        "delivery_events",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "delivery_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("deliveries.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column(
            "event_time",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column(
            "details_jsonb",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_delivery_events_delivery_id",
        "delivery_events",
        ["delivery_id"],
        unique=False,
    )
    op.create_index(
        "ix_delivery_events_event_time",
        "delivery_events",
        ["event_time"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_delivery_events_event_time", table_name="delivery_events")
    op.drop_index("ix_delivery_events_delivery_id", table_name="delivery_events")
    op.drop_table("delivery_events")

    op.drop_index("ix_deliveries_status", table_name="deliveries")
    op.drop_index("ix_deliveries_invoice_id", table_name="deliveries")
    op.drop_index("ix_deliveries_enquiry_id", table_name="deliveries")
    op.drop_table("deliveries")

    op.drop_index("ix_payments_invoice_id", table_name="payments")
    op.drop_table("payments")

    op.drop_index("ix_invoices_status", table_name="invoices")
    op.drop_index("ix_invoices_customer_po_id", table_name="invoices")
    op.drop_index("ix_invoices_enquiry_id", table_name="invoices")
    op.drop_table("invoices")

    op.drop_index("ix_rtm_pos_status", table_name="rtm_pos")
    op.drop_index("ix_rtm_pos_manufacturer_id", table_name="rtm_pos")
    op.drop_index("ix_rtm_pos_quotation_revision_id", table_name="rtm_pos")
    op.drop_index("ix_rtm_pos_enquiry_id", table_name="rtm_pos")
    op.drop_table("rtm_pos")

    op.drop_index("ix_customer_pos_status", table_name="customer_pos")
    op.drop_index("ix_customer_pos_customer_id", table_name="customer_pos")
    op.drop_index("ix_customer_pos_quotation_revision_id", table_name="customer_pos")
    op.drop_index("ix_customer_pos_enquiry_id", table_name="customer_pos")
    op.drop_table("customer_pos")
