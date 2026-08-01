from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.constants import DEFAULT_ROLE_NAMES
from app.domain.entities.enums import RoleName
from app.domain.entities.role import Role
from app.domain.entities.user import User
from app.domain.entities.user_role import UserRole
from app.domain.repositories.role_repository import RoleRepository


class SqlAlchemyRoleRepository(RoleRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_name(self, name: RoleName | str) -> Role | None:
        normalized = name if isinstance(name, RoleName) else RoleName(name)
        return self._session.scalar(select(Role).where(Role.name == normalized))

    def list_by_user_id(self, user_id: int) -> list[Role]:
        statement = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .order_by(Role.name)
        )
        return list(self._session.scalars(statement))

    def assign_to_user(self, user: User, role: Role) -> None:
        if user.id is None:
            self._session.flush()
        exists = self._session.scalar(
            select(UserRole.id).where(
                UserRole.user_id == user.id,
                UserRole.role_id == role.id,
            )
        )
        if exists is None:
            self._session.add(UserRole(user_id=user.id, role_id=role.id))

    def remove_from_user(self, user_id: int, role_id: int) -> None:
        self._session.execute(
            delete(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )

    def create_default_roles(self) -> list[Role]:
        roles: list[Role] = []
        for name in DEFAULT_ROLE_NAMES:
            parsed = RoleName(name)
            role = self.get_by_name(parsed)
            if role is None:
                role = Role(name=parsed, description=f"NeuroTech {name.replace('_', ' ')} role")
                self._session.add(role)
                self._session.flush()
            roles.append(role)
        return roles
