from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class FutureEntityRepository(ABC):
    """Read-oriented Phase 2 port; workflows and concrete adapters are intentionally deferred."""

    @abstractmethod
    def get_by_public_id(self, public_id: str) -> Any | None: ...


class ProductRepository(FutureEntityRepository):
    pass


class CourseRepository(FutureEntityRepository):
    pass


class EventRepository(FutureEntityRepository):
    pass


class PartnerRepository(FutureEntityRepository):
    pass


class TradeRepository(FutureEntityRepository):
    pass


class OrderRepository(FutureEntityRepository):
    pass
