from sqlalchemy import exists, or_, select
from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _active_select():
        return select(User).where(User.deleted_at.is_(None))

    def get_by_id(self, user_id: int) -> User | None:
        return self._session.scalar(self._active_select().where(User.id == user_id))

    def get_by_public_id(self, public_id: str) -> User | None:
        return self._session.scalar(self._active_select().where(User.public_id == public_id))

    def get_by_email(self, email: str) -> User | None:
        return self._session.scalar(self._active_select().where(User.email == email))

    def get_by_phone(self, phone: str) -> User | None:
        return self._session.scalar(self._active_select().where(User.phone == phone))

    def exists_by_email(self, email: str) -> bool:
        return bool(self._session.scalar(select(exists().where(User.email == email))))

    def exists_by_phone(self, phone: str) -> bool:
        return bool(self._session.scalar(select(exists().where(User.phone == phone))))

    def add(self, user: User) -> User:
        self._session.add(user)
        return user

    def update(self, user: User) -> User:
        self._session.add(user)
        return user
