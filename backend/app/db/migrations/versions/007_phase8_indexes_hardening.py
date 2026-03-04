"""007_phase8_indexes_hardening

Revision ID: 007_phase8_indexes_hardening
Revises: 006_po_invoice_payment_delivery
Create Date: 2026-03-04 20:25:00

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "007_phase8_indexes_hardening"
down_revision: str | None = "006_po_invoice_payment_delivery"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index("ix_enquiry_items_product_id", "enquiry_items", ["product_id"], unique=False)
    op.create_index(
        "ix_enquiry_status_history_changed_by",
        "enquiry_status_history",
        ["changed_by"],
        unique=False,
    )
    op.create_index(
        "ix_quotation_revisions_created_by",
        "quotation_revisions",
        ["created_by"],
        unique=False,
    )
    op.create_index(
        "ix_quotation_items_enquiry_item_id",
        "quotation_items",
        ["enquiry_item_id"],
        unique=False,
    )
    op.create_index(
        "ix_quotation_items_product_id",
        "quotation_items",
        ["product_id"],
        unique=False,
    )
    op.create_index("ix_approvals_decided_by", "approvals", ["decided_by"], unique=False)

    op.create_index("ix_customer_pos_po_date", "customer_pos", ["po_date"], unique=False)
    op.create_index("ix_rtm_pos_po_date", "rtm_pos", ["po_date"], unique=False)
    op.create_index("ix_invoices_issue_date", "invoices", ["issue_date"], unique=False)
    op.create_index("ix_payments_payment_date", "payments", ["payment_date"], unique=False)
    op.create_index(
        "ix_delivery_events_created_by",
        "delivery_events",
        ["created_by"],
        unique=False,
    )

    op.create_index("ix_audit_events_request_id", "audit_events", ["request_id"], unique=False)
    op.create_index("ix_audit_events_created_at", "audit_events", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_events_created_at", table_name="audit_events")
    op.drop_index("ix_audit_events_request_id", table_name="audit_events")

    op.drop_index("ix_delivery_events_created_by", table_name="delivery_events")
    op.drop_index("ix_payments_payment_date", table_name="payments")
    op.drop_index("ix_invoices_issue_date", table_name="invoices")
    op.drop_index("ix_rtm_pos_po_date", table_name="rtm_pos")
    op.drop_index("ix_customer_pos_po_date", table_name="customer_pos")

    op.drop_index("ix_approvals_decided_by", table_name="approvals")
    op.drop_index("ix_quotation_items_product_id", table_name="quotation_items")
    op.drop_index("ix_quotation_items_enquiry_item_id", table_name="quotation_items")
    op.drop_index("ix_quotation_revisions_created_by", table_name="quotation_revisions")
    op.drop_index("ix_enquiry_status_history_changed_by", table_name="enquiry_status_history")
    op.drop_index("ix_enquiry_items_product_id", table_name="enquiry_items")
