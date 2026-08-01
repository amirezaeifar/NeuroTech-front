import pytest

from app.core.normalization import normalize_email, normalize_phone


def test_email_normalization():
    assert normalize_email("  USER@Example.COM ") == "user@example.com"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("09121234567", "+989121234567"),
        ("+98 912 123 4567", "+989121234567"),
        ("0098-912-123-4567", "+989121234567"),
    ],
)
def test_phone_normalization(raw, expected):
    assert normalize_phone(raw) == expected


def test_invalid_phone_rejected():
    with pytest.raises(ValueError):
        normalize_phone("123")
