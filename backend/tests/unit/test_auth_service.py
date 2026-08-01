import pytest

from app.core.exceptions import AuthenticationError, DuplicateResourceError, TokenReuseDetected
from app.domain.entities.enums import UserStatus
from app.domain.services.auth_service import ClientContext


def _registration(email="member@example.com", phone="+989121234567"):
    return {
        "first_name": "Nima",
        "last_name": "Karimi",
        "email": email,
        "phone": phone,
        "password": "strong-password",
        "preferred_locale": "fa",
    }


def test_registration_normalizes_and_assigns_only_user_role(auth_service, fake_state):
    user = auth_service.register(_registration(email="MEMBER@EXAMPLE.COM"))
    assert user["email"] == "member@example.com"
    assert user["roles"] == ["user"]
    assert [link.role_id for link in fake_state.user_roles]


def test_duplicate_email_and_phone_are_rejected(auth_service):
    auth_service.register(_registration())
    with pytest.raises(DuplicateResourceError):
        auth_service.register(_registration(phone="+989121234568"))
    with pytest.raises(DuplicateResourceError):
        auth_service.register(_registration(email="other@example.com"))


def test_login_uses_generic_failure_and_rejects_suspended(auth_service, fake_state):
    auth_service.register(_registration())
    with pytest.raises(AuthenticationError, match="Invalid credentials"):
        auth_service.login("absent@example.com", "strong-password")
    with pytest.raises(AuthenticationError, match="Invalid credentials"):
        auth_service.login("member@example.com", "wrong-password")
    fake_state.users[0].status = UserStatus.SUSPENDED
    with pytest.raises(AuthenticationError, match="Account is unavailable"):
        auth_service.login("member@example.com", "strong-password")


def test_refresh_rotation_and_reuse_detection(auth_service, fake_state):
    auth_service.register(_registration())
    first = auth_service.login(
        "member@example.com",
        "strong-password",
        ClientContext("127.0.0.1", "pytest"),
    )
    rotated = auth_service.refresh_session(first["refresh_token"])
    assert rotated["access_token"] != first["access_token"]
    assert len(fake_state.refresh_tokens) == 2
    assert fake_state.refresh_tokens[0].revoked_at is not None
    assert fake_state.refresh_tokens[0].replaced_by_jti == fake_state.refresh_tokens[1].jti
    with pytest.raises(TokenReuseDetected):
        auth_service.refresh_session(first["refresh_token"])
    assert fake_state.users[0].token_version == 1
    assert all(token.revoked_at is not None for token in fake_state.refresh_tokens)


def test_logout_logout_all_and_password_change(auth_service, fake_state):
    user = auth_service.register(_registration())
    first = auth_service.login("member@example.com", "strong-password")
    auth_service.logout(first["refresh_token"])
    assert fake_state.refresh_tokens[0].revoked_at is not None
    second = auth_service.login("member@example.com", "strong-password")
    auth_service.logout_all(user["public_id"])
    assert fake_state.users[0].token_version == 1
    assert fake_state.refresh_tokens[-1].revoked_at is not None
    third = auth_service.login("member@example.com", "strong-password")
    auth_service.change_password(user["public_id"], "strong-password", "new-strong-password")
    assert fake_state.users[0].token_version == 2
    assert fake_state.refresh_tokens[-1].revoked_at is not None
    with pytest.raises(AuthenticationError):
        auth_service.login("member@example.com", "strong-password")
    assert auth_service.login("member@example.com", "new-strong-password")["access_token"]
