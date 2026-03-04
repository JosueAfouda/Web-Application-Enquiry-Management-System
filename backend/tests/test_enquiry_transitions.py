from app.schemas.enquiries import EnquiryStatus
from app.services.enquiries_service import is_transition_allowed


def test_valid_transition() -> None:
    assert is_transition_allowed(EnquiryStatus.RECEIVED.value, EnquiryStatus.IN_REVIEW.value)
    assert is_transition_allowed(EnquiryStatus.IN_DELIVERY.value, EnquiryStatus.DELIVERED.value)


def test_invalid_transition() -> None:
    assert not is_transition_allowed(
        EnquiryStatus.RECEIVED.value,
        EnquiryStatus.APPROVED.value,
    )
    assert not is_transition_allowed(
        EnquiryStatus.CLOSED.value,
        EnquiryStatus.IN_REVIEW.value,
    )
