from __future__ import annotations

import pytest
from http.cookies import SimpleCookie

from flask import g
from sqlalchemy import create_engine, select
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.domain.entities import Base
from app.domain.entities.enums import UserStatus
from app.domain.entities.user import User
from app.core.responses import success_response
from app.infrastructure.db.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from app.interfaces.http.authentication import roles_required
from app.main import create_app
from tests.fakes import CapturingOtpSender, FrozenClock, MemoryOtpStore, PingRedis


@pytest.fixture
def app():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    registry = scoped_session(
        sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
    )
    clock = FrozenClock()
    store = MemoryOtpStore(clock)
    application = create_app(
        {
            "TESTING": True,
            "DATABASE_URL": "sqlite://",
            "ENGINE": engine,
            "SESSION_REGISTRY": registry,
            "REDIS_CLIENT": PingRedis(),
            "CLOCK": clock,
            "OTP_STORE": store,
            "SECRET_KEY": "functional-secret",
            "JWT_SECRET": "functional-jwt-secret",
            "OTP_DEVELOPMENT_MODE": True,
        }
    )
    application.extensions["auth_service"].create_default_roles()
    application.extensions["test_clock"] = clock

    @application.get("/_test/admin-only")
    @roles_required("admin")
    def admin_only():
        return success_response({"roles": list(g.auth_context.roles)})

    yield application
    registry.remove()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(app):
    return app.test_client()


def _register(client, email="member@example.com", phone="+989121234567"):
    return client.post(
        "/auth/register",
        json={
            "first_name": "Nima",
            "last_name": "Karimi",
            "email": email,
            "phone": phone,
            "password": "strong-password",
            "preferred_locale": "fa",
        },
    )


def _login(client):
    return client.post(
        "/auth/login",
        json={"identifier": "member@example.com", "password": "strong-password"},
    )


def test_health_and_standard_response(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["success"] is True
    assert response.json["data"]["dependencies"] == {"database": "ok", "redis": "ok"}


def test_registration_validation_and_duplicates(client):
    response = _register(client)
    assert response.status_code == 201
    assert "id" not in response.json["data"]
    assert response.json["data"]["roles"] == ["user"]
    duplicate_email = _register(client, phone="+989121234568")
    duplicate_phone = _register(client, email="other@example.com")
    assert duplicate_email.status_code == 409
    assert duplicate_phone.status_code == 409
    privileged = client.post(
        "/auth/register",
        json={
            "first_name": "Bad",
            "last_name": "Actor",
            "email": "bad@example.com",
            "password": "strong-password",
            "is_admin": True,
        },
    )
    assert privileged.status_code == 422
    assert privileged.json["success"] is False


def test_password_access_refresh_logout_and_me(client):
    _register(client)
    invalid = client.post(
        "/auth/login",
        json={"identifier": "member@example.com", "password": "wrong-password"},
    )
    assert invalid.status_code == 401
    login = _login(client)
    assert login.status_code == 200
    access = login.json["data"]["access_token"]
    cookie = login.headers.get("Set-Cookie", "")
    assert "HttpOnly" in cookie
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200
    assert me.json["data"]["email"] == "member@example.com"
    refreshed = client.post("/auth/refresh")
    assert refreshed.status_code == 200
    assert refreshed.json["data"]["access_token"] != access
    logout = client.post("/auth/logout")
    assert logout.status_code == 200
    assert "Max-Age=0" in logout.headers.get("Set-Cookie", "")


def test_revoked_refresh_reuse_revokes_family(client):
    _register(client)
    login = _login(client)
    cookie_name = "neurotech_refresh_token"
    parsed = SimpleCookie()
    parsed.load(login.headers["Set-Cookie"])
    old_refresh = parsed[cookie_name].value
    assert client.post("/auth/refresh").status_code == 200
    client.set_cookie(cookie_name, old_refresh, path="/auth")
    reused = client.post("/auth/refresh")
    assert reused.status_code == 401
    assert "reuse detected" in reused.json["message"].lower()


def test_logout_all_and_change_password_invalidate_tokens(client):
    _register(client)
    login = _login(client)
    access = login.json["data"]["access_token"]
    changed = client.post(
        "/auth/change-password",
        headers={"Authorization": f"Bearer {access}"},
        json={
            "current_password": "strong-password",
            "new_password": "new-strong-password",
        },
    )
    assert changed.status_code == 200
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {access}"}).status_code == 401
    old_login = _login(client)
    assert old_login.status_code == 401
    new_login = client.post(
        "/auth/login",
        json={"identifier": "member@example.com", "password": "new-strong-password"},
    )
    new_access = new_login.json["data"]["access_token"]
    logout_all = client.post(
        "/auth/logout-all", headers={"Authorization": f"Bearer {new_access}"}
    )
    assert logout_all.status_code == 200


def test_otp_request_verification_and_reuse(client):
    _register(client, email=None)
    requested = client.post(
        "/auth/request-otp",
        json={"destination": "09121234567", "purpose": "login"},
    )
    assert requested.status_code == 200
    code = requested.json["data"]["development_otp"]
    verified = client.post(
        "/auth/verify-otp",
        json={"destination": "09121234567", "purpose": "login", "code": code},
    )
    assert verified.status_code == 200
    assert verified.json["data"]["access_token"]
    reused = client.post(
        "/auth/verify-otp",
        json={"destination": "09121234567", "purpose": "login", "code": code},
    )
    assert reused.status_code == 400


def test_otp_expiry_and_maximum_attempts(client, app):
    expired = client.post(
        "/auth/request-otp",
        json={"destination": "09121234567", "purpose": "registration"},
    )
    code = expired.json["data"]["development_otp"]
    app.extensions["test_clock"].advance(seconds=121)
    assert (
        client.post(
            "/auth/verify-otp",
            json={"destination": "09121234567", "purpose": "registration", "code": code},
        ).status_code
        == 400
    )

    destination = "09121234568"
    client.post(
        "/auth/request-otp",
        json={"destination": destination, "purpose": "registration"},
    )
    for attempt in range(4):
        response = client.post(
            "/auth/verify-otp",
            json={
                "destination": destination,
                "purpose": "registration",
                "code": f"00000{attempt}",
            },
        )
        assert response.status_code == 400
    final = client.post(
        "/auth/verify-otp",
        json={"destination": destination, "purpose": "registration", "code": "000004"},
    )
    assert final.status_code == 429


@pytest.mark.parametrize("status", [UserStatus.SUSPENDED, UserStatus.DISABLED])
def test_suspended_and_disabled_users_cannot_login(client, app, status):
    _register(client)
    registry = app.extensions["session_registry"]
    with registry() as session:
        user = session.scalar(select(User).where(User.email == "member@example.com"))
        user.status = status
        session.commit()
    response = _login(client)
    assert response.status_code == 401
    assert response.json["message"] == "Account is unavailable."


def test_role_authorization_reads_current_database_roles(client, app):
    _register(client)
    login = _login(client)
    access = login.json["data"]["access_token"]
    denied = client.get(
        "/_test/admin-only", headers={"Authorization": f"Bearer {access}"}
    )
    assert denied.status_code == 403

    app.extensions["auth_service"].create_admin(
        {
            "first_name": "Nima",
            "last_name": "Karimi",
            "email": "member@example.com",
            "phone": "+989121234567",
            "password": "",
            "preferred_locale": "fa",
        }
    )
    admin_login = _login(client)
    allowed = client.get(
        "/_test/admin-only",
        headers={"Authorization": f"Bearer {admin_login.json['data']['access_token']}"},
    )
    assert allowed.status_code == 200
