import pytest

from app.core.exceptions import OtpAttemptsExceeded, OtpCooldownError, OtpError, OtpRateLimitError
from app.domain.services.otp_service import OtpService
from tests.fakes import CapturingOtpSender, MemoryOtpStore


def _service(clock, auth_service, *, max_attempts=3, max_requests=2):
    store = MemoryOtpStore(clock)
    sender = CapturingOtpSender()
    service = OtpService(
        store,
        sender,
        clock,
        auth_service,
        hash_secret="otp-test-secret",
        expire_seconds=120,
        resend_cooldown_seconds=60,
        max_attempts=max_attempts,
        max_requests_per_hour=max_requests,
        code_length=6,
        development_mode=True,
    )
    return service, store, sender


def test_otp_creation_verification_and_single_use(clock, auth_service):
    auth_service.register(
        {
            "first_name": "Nima",
            "last_name": "Karimi",
            "email": None,
            "phone": "+989121234567",
            "password": "strong-password",
            "preferred_locale": "fa",
        }
    )
    service, store, sender = _service(clock, auth_service)
    requested = service.request_otp("09121234567", "login")
    assert requested["development_otp"].isdigit()
    assert len(sender.sent) == 1
    session = service.verify_otp("09121234567", "login", requested["development_otp"])
    assert session["access_token"]
    with pytest.raises(OtpError):
        service.verify_otp("09121234567", "login", requested["development_otp"])


def test_otp_cooldown_attempt_limit_expiry_and_hourly_limit(clock, auth_service):
    service, store, sender = _service(clock, auth_service)
    service.request_otp("09121234567", "registration")
    with pytest.raises(OtpCooldownError):
        service.request_otp("09121234567", "registration")
    with pytest.raises(OtpError):
        service.verify_otp("09121234567", "registration", "000000")
    with pytest.raises(OtpError):
        service.verify_otp("09121234567", "registration", "000001")
    with pytest.raises(OtpAttemptsExceeded):
        service.verify_otp("09121234567", "registration", "000002")
    clock.advance(seconds=61)
    service.request_otp("09121234567", "registration")
    clock.advance(seconds=61)
    with pytest.raises(OtpRateLimitError):
        service.request_otp("09121234567", "registration")
    clock.advance(hours=1)
    requested = service.request_otp("09121234567", "registration")
    clock.advance(seconds=121)
    with pytest.raises(OtpError):
        service.verify_otp("09121234567", "registration", requested["development_otp"])
