from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.enums import RoleName
from app.domain.entities.role import Role
from app.domain.entities.user import User


class RoleRepository(ABC):
    @abstractmethod
    def get_by_name(self, name: RoleName | str) -> Role | None: ...

    @abstractmethod
    def list_by_user_id(self, user_id: int) -> list[Role]: ...

    @abstractmethod
    def assign_to_user(self, user: User, role: Role) -> None: ...

    @abstractmethod
    def remove_from_user(self, user_id: int, role_id: int) -> None: ...

    @abstractmethod
    def create_default_roles(self) -> list[Role]: ...
