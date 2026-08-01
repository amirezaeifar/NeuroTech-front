from __future__ import annotations

from datetime import datetime

import pytest

from app.domain.services.auth_service import AuthService
from app.infrastructure.security.pyjwt_token_service import PyJwtTokenService
from app.infrastructure.security.werkzeug_password_hasher import WerkzeugPasswordHasher
from tests.fakes import FakeState, FakeUowFactory, FrozenClock


@pytest.fixture
def clock():
    return FrozenClock(datetime(2026, 1, 1, 12, 0, 0))


@pytest.fixture
def fake_state():
    return FakeState()


@pytest.fixture
def token_service(clock):
    return PyJwtTokenService(
        "test-jwt-secret-with-sufficient-length",
        "HS256",
        "neurotech",
        "neurotech-users",
        15,
        30,
        0,
        clock,
    )


@pytest.fixture
def auth_service(fake_state, clock, token_service):
    factory = FakeUowFactory(fake_state, clock)
    service = AuthService(factory, WerkzeugPasswordHasher(), token_service, clock)
    service.create_default_roles()
    return service
