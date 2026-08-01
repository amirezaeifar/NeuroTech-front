from __future__ import annotations

from types import TracebackType
from typing import Callable

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import DuplicateResourceError, InfrastructureError
from app.domain.unit_of_work import UnitOfWork
from app.infrastructure.repositories.refresh_token_sqlalchemy import SqlAlchemyRefreshTokenRepository
from app.infrastructure.repositories.role_sqlalchemy import SqlAlchemyRoleRepository
from app.infrastructure.repositories.user_sqlalchemy import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory
        self.session: Session | None = None
        self._committed = False

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self._session_factory()
        self.users = SqlAlchemyUserRepository(self.session)
        self.roles = SqlAlchemyRoleRepository(self.session)
        self.refresh_tokens = SqlAlchemyRefreshTokenRepository(self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self.session is None:
            return
        try:
            if exc_type is not None or not self._committed:
                self.session.rollback()
        finally:
            self.session.close()
            self.session = None

    def commit(self) -> None:
        try:
            self._require_session().commit()
            self._committed = True
        except IntegrityError as exc:
            self._require_session().rollback()
            raise DuplicateResourceError("The resource conflicts with existing data.") from exc
        except SQLAlchemyError as exc:
            self._require_session().rollback()
            raise InfrastructureError("A database operation could not be completed.") from exc

    def rollback(self) -> None:
        self._require_session().rollback()

    def flush(self) -> None:
        try:
            self._require_session().flush()
        except IntegrityError as exc:
            self._require_session().rollback()
            raise DuplicateResourceError("The resource conflicts with existing data.") from exc
        except SQLAlchemyError as exc:
            self._require_session().rollback()
            raise InfrastructureError("A database operation could not be completed.") from exc

    def _require_session(self) -> Session:
        if self.session is None:
            raise RuntimeError("Unit of Work must be used as a context manager.")
        return self.session
