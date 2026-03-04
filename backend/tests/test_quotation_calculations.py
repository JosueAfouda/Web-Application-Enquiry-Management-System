from decimal import Decimal

from app.schemas.quotations import QuotationRevisionCreateRequest, QuotationRevisionItemCreate
from app.services.quotations_service import QuotationService


def test_subtotal_and_total_calculation() -> None:
    payload = QuotationRevisionCreateRequest(
        freight=Decimal("12.50"),
        markup_percent=Decimal("10.0"),
        currency="USD",
        items=[
            QuotationRevisionItemCreate(
                product_id="00000000-0000-0000-0000-000000000001",
                qty=Decimal("2"),
                unit_price=Decimal("10.00"),
            ),
            QuotationRevisionItemCreate(
                product_id="00000000-0000-0000-0000-000000000002",
                qty=Decimal("3"),
                unit_price=Decimal("5.00"),
            ),
        ],
    )

    subtotal = QuotationService._calculate_subtotal(payload)
    total = QuotationService._calculate_total(subtotal, payload.freight, payload.markup_percent)

    assert subtotal == Decimal("35.00")
    assert total == Decimal("51.00")


def test_quantize_rounding() -> None:
    assert QuotationService._quantize(Decimal("1.005")) == Decimal("1.01")
