from abc import ABC, abstractmethod


class OtpSender(ABC):
    @abstractmethod
    def send(self, destination: str, code: str, purpose: str) -> None: ...
