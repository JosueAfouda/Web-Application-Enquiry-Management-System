from decimal import Decimal

from app.schemas.commercial import DeliveryCreateRequest, DeliveryStatus
from app.services.commercial_service import CommercialService


def test_derive_invoice_status() -> None:
    total = Decimal("100.00")
    assert CommercialService.derive_invoice_status(total, Decimal("0")) == "UNPAID"
    assert CommercialService.derive_invoice_status(total, Decimal("10.00")) == "PARTIAL"
    assert CommercialService.derive_invoice_status(total, Decimal("100.00")) == "PAID"


def test_resolve_delivery_status() -> None:
    pending_payload = DeliveryCreateRequest(
        enquiry_id="00000000-0000-0000-0000-000000000001",
    )
    assert (
        CommercialService._resolve_delivery_status(pending_payload) == DeliveryStatus.PENDING.value
    )

    shipped_payload = DeliveryCreateRequest(
        enquiry_id="00000000-0000-0000-0000-000000000001",
        shipped_at="2026-03-04T20:00:00Z",
    )
    assert (
        CommercialService._resolve_delivery_status(shipped_payload)
        == DeliveryStatus.IN_TRANSIT.value
    )
