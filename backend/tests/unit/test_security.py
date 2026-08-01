import pytest

from app.core.exceptions import TokenError
from app.infrastructure.security.werkzeug_password_hasher import WerkzeugPasswordHasher


def test_password_hashing_never_returns_plaintext():
    hasher = WerkzeugPasswordHasher()
    encoded = hasher.hash("correct horse battery staple")
    assert encoded != "correct horse battery staple"
    assert hasher.verify(encoded, "correct horse battery staple")
    assert not hasher.verify(encoded, "wrong")


def test_access_and_refresh_claims(token_service):
    access = token_service.create_access_token("public-user-id", ["user"], 3)
    refresh = token_service.create_refresh_token("public-user-id", 3)
    access_claims = token_service.decode(access.raw, expected_type="access")
    refresh_claims = token_service.decode(refresh.raw, expected_type="refresh")
    assert access_claims["sub"] == "public-user-id"
    assert access_claims["roles"] == ["user"]
    assert access_claims["token_version"] == 3
    assert refresh_claims["family"]
    assert token_service.hash_token(refresh.raw) != refresh.raw


def test_token_type_cannot_be_confused(token_service):
    access = token_service.create_access_token("public-user-id", ["user"], 0)
    with pytest.raises(TokenError):
        token_service.decode(access.raw, expected_type="refresh")
