from abc import ABC, abstractmethod


class HealthProbe(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def check(self) -> None: ...
