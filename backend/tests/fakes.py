from __future__ import annotations

import hmac
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from types import TracebackType

from app.core.exceptions import OtpCooldownError, OtpRateLimitError
from app.domain.entities.enums import RoleName
from app.domain.entities.refresh_token import RefreshToken
from app.domain.entities.role import Role
from app.domain.entities.user import User
from app.domain.entities.user_role import UserRole
from app.domain.ports.clock import Clock
from app.domain.ports.otp_sender import OtpSender
from app.domain.ports.otp_store import OtpRecord, OtpStore, OtpVerificationStatus
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.repositories.role_repository import RoleRepository
from app.domain.repositories.user_repository import UserRepository
from app.domain.unit_of_work import UnitOfWork


class FrozenClock(Clock):
    def __init__(self, now: datetime | None = None) -> None:
        self.current = now or datetime(2026, 1, 1, 12, 0, 0)

    def now(self) -> datetime:
        return self.current

    def advance(self, **kwargs) -> None:
        self.current += timedelta(**kwargs)


@dataclass
class FakeState:
    users: list[User] = field(default_factory=list)
    roles: list[Role] = field(default_factory=list)
    user_roles: list[UserRole] = field(default_factory=list)
    refresh_tokens: list[RefreshToken] = field(default_factory=list)
    next_user_id: int = 1
    next_role_id: int = 1
    next_refresh_id: int = 1


class FakeUserRepository(UserRepository):
    def __init__(self, state: FakeState, clock: Clock) -> None:
        self.state = state
        self.clock = clock

    def _available(self, user: User) -> bool:
        return user.deleted_at is None

    def get_by_id(self, user_id: int) -> User | None:
        return next((u for u in self.state.users if u.id == user_id and self._available(u)), None)

    def get_by_public_id(self, public_id: str) -> User | None:
        return next((u for u in self.state.users if u.public_id == public_id and self._available(u)), None)

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self.state.users if u.email == email and self._available(u)), None)

    def get_by_phone(self, phone: str) -> User | None:
        return next((u for u in self.state.users if u.phone == phone and self._available(u)), None)

    def exists_by_email(self, email: str) -> bool:
        return any(u.email == email for u in self.state.users)

    def exists_by_phone(self, phone: str) -> bool:
        return any(u.phone == phone for u in self.state.users)

    def add(self, user: User) -> User:
        if user.id is None:
            user.id = self.state.next_user_id
            self.state.next_user_id += 1
        if user.public_id is None:
            user.public_id = str(uuid.uuid4())
        if user.created_at is None:
            user.created_at = self.clock.now()
        if user.updated_at is None:
            user.updated_at = self.clock.now()
        self.state.users.append(user)
        return user

    def update(self, user: User) -> User:
        return user


class FakeRoleRepository(RoleRepository):
    def __init__(self, state: FakeState, clock: Clock) -> None:
        self.state = state
        self.clock = clock

    def get_by_name(self, name: RoleName | str) -> Role | None:
        parsed = name if isinstance(name, RoleName) else RoleName(name)
        return next((role for role in self.state.roles if role.name == parsed), None)

    def list_by_user_id(self, user_id: int) -> list[Role]:
        role_ids = {link.role_id for link in self.state.user_roles if link.user_id == user_id}
        return [role for role in self.state.roles if role.id in role_ids]

    def assign_to_user(self, user: User, role: Role) -> None:
        if not any(
            link.user_id == user.id and link.role_id == role.id
            for link in self.state.user_roles
        ):
            self.state.user_roles.append(UserRole(user_id=user.id, role_id=role.id))

    def remove_from_user(self, user_id: int, role_id: int) -> None:
        self.state.user_roles = [
            link
            for link in self.state.user_roles
            if not (link.user_id == user_id and link.role_id == role_id)
        ]

    def create_default_roles(self) -> list[Role]:
        for name in RoleName:
            if self.get_by_name(name) is None:
                role = Role(
                    id=self.state.next_role_id,
                    name=name,
                    description=name.value,
                    created_at=self.clock.now(),
                    updated_at=self.clock.now(),
                )
                self.state.next_role_id += 1
                self.state.roles.append(role)
        return list(self.state.roles)


class FakeRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, state: FakeState, clock: Clock) -> None:
        self.state = state
        self.clock = clock

    def get_by_jti(self, jti: str) -> RefreshToken | None:
        return next((token for token in self.state.refresh_tokens if token.jti == jti), None)

    def add(self, token: RefreshToken) -> RefreshToken:
        token.id = self.state.next_refresh_id
        self.state.next_refresh_id += 1
        token.public_id = token.public_id or str(uuid.uuid4())
        token.created_at = token.created_at or self.clock.now()
        self.state.refresh_tokens.append(token)
        return token

    def revoke(self, token, revoked_at, *, replaced_by_jti=None) -> None:
        token.revoked_at = revoked_at
        token.replaced_by_jti = replaced_by_jti

    def revoke_family(self, token_family, revoked_at) -> int:
        changed = 0
        for token in self.state.refresh_tokens:
            if token.token_family == token_family and token.revoked_at is None:
                token.revoked_at = revoked_at
                changed += 1
        return changed

    def revoke_all_for_user(self, user_id, revoked_at) -> int:
        changed = 0
        for token in self.state.refresh_tokens:
            if token.user_id == user_id and token.revoked_at is None:
                token.revoked_at = revoked_at
                changed += 1
        return changed

    def list_active_for_user(self, user_id, now):
        return [
            token
            for token in self.state.refresh_tokens
            if token.user_id == user_id
            and token.revoked_at is None
            and token.expires_at > now
        ]


class FakeUnitOfWork(UnitOfWork):
    def __init__(self, state: FakeState, clock: Clock) -> None:
        self.state = state
        self.users = FakeUserRepository(state, clock)
        self.roles = FakeRoleRepository(state, clock)
        self.refresh_tokens = FakeRefreshTokenRepository(state, clock)
        self.committed = False
        self.rolled_back = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if exc_type is not None or not self.committed:
            self.rollback()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def flush(self) -> None:
        return None


class FakeUowFactory:
    def __init__(self, state: FakeState, clock: Clock) -> None:
        self.state = state
        self.clock = clock
        self.instances: list[FakeUnitOfWork] = []

    def __call__(self) -> FakeUnitOfWork:
        instance = FakeUnitOfWork(self.state, self.clock)
        self.instances.append(instance)
        return instance


class MemoryOtpStore(OtpStore):
    def __init__(self, clock: Clock) -> None:
        self.clock = clock
        self.records: dict[tuple[str, str], OtpRecord] = {}
        self.rates: dict[str, tuple[int, datetime]] = {}

    def create(self, record, *, ttl_seconds, max_requests_per_hour) -> None:
        key = (record.purpose, record.destination)
        existing = self.records.get(key)
        if existing and existing.expires_at > self.clock.now():
            if existing.resend_available_at > self.clock.now():
                raise OtpCooldownError("Please wait before requesting another code.")
        count, window = self.rates.get(record.destination, (0, self.clock.now()))
        if self.clock.now() >= window + timedelta(hours=1):
            count, window = 0, self.clock.now()
        count += 1
        self.rates[record.destination] = (count, window)
        if count > max_requests_per_hour:
            raise OtpRateLimitError("OTP request limit exceeded.")
        self.records[key] = record

    def verify_and_consume(self, purpose, destination, candidate_hash):
        key = (purpose, destination)
        record = self.records.get(key)
        if record is None or record.expires_at <= self.clock.now():
            self.records.pop(key, None)
            return OtpVerificationStatus.MISSING
        if record.attempt_count >= record.max_attempts:
            self.records.pop(key, None)
            return OtpVerificationStatus.ATTEMPTS_EXCEEDED
        if hmac.compare_digest(record.code_hash, candidate_hash):
            self.records.pop(key, None)
            return OtpVerificationStatus.VERIFIED
        updated = OtpRecord(
            purpose=record.purpose,
            destination=record.destination,
            code_hash=record.code_hash,
            created_at=record.created_at,
            expires_at=record.expires_at,
            attempt_count=record.attempt_count + 1,
            max_attempts=record.max_attempts,
            request_count=record.request_count,
            resend_available_at=record.resend_available_at,
        )
        self.records[key] = updated
        if updated.attempt_count >= updated.max_attempts:
            self.records.pop(key, None)
            return OtpVerificationStatus.ATTEMPTS_EXCEEDED
        return OtpVerificationStatus.INVALID

    def consume(self, purpose: str, destination: str) -> None:
        self.records.pop((purpose, destination), None)


class CapturingOtpSender(OtpSender):
    def __init__(self) -> None:
        self.sent: list[tuple[str, str, str]] = []

    def send(self, destination: str, code: str, purpose: str) -> None:
        self.sent.append((destination, code, purpose))


class PingRedis:
    def ping(self) -> bool:
        return True
