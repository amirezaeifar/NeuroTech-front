from app.domain.ports.otp_sender import OtpSender


class DevelopmentOtpSender(OtpSender):
    """Development-only sender; intentionally performs no external delivery or logging."""

    def send(self, destination: str, code: str, purpose: str) -> None:
        return None
