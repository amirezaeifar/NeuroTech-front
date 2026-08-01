from __future__ import annotations

import hmac
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from app.core.exceptions import (
    AuthenticationError,
    DuplicateResourceError,
    ResourceNotFoundError,
    TokenError,
    TokenReuseDetected,
    ValidationAppError,
)
from app.core.normalization import normalize_destination, normalize_email, normalize_phone
from app.domain.entities.enums import RoleName, UserStatus
from app.domain.entities.refresh_token import RefreshToken
from app.domain.entities.user import User
from app.domain.ports.clock import Clock
from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.token_service import EncodedToken, TokenService
from app.domain.unit_of_work import UnitOfWork

UowFactory = Callable[[], UnitOfWork]


@dataclass(frozen=True, slots=True)
class ClientContext:
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True, slots=True)
class AuthContext:
    user_public_id: str
    roles: tuple[str, ...]
    token_version: int


class AuthService:
    def __init__(
        self,
        uow_factory: UowFactory,
        password_hasher: PasswordHasher,
        token_service: TokenService,
        clock: Clock,
        *,
        password_min_length: int = 8,
    ) -> None:
        self._uow_factory = uow_factory
        self._password_hasher = password_hasher
        self._tokens = token_service
        self._clock = clock
        self._password_min_length = password_min_length

    def register(self, values: dict[str, Any]) -> dict[str, Any]:
        email = self._normalize_email(values.get("email"))
        phone = self._normalize_phone(values.get("phone"))
        if not email and not phone:
            raise ValidationAppError(
                "At least one contact method is required.",
                errors={"_schema": ["Provide an email address or phone number."]},
            )
        password = str(values.get("password", ""))
        self._validate_password(password)
        with self._uow_factory() as uow:
            if email and uow.users.exists_by_email(email):
                raise DuplicateResourceError("An account already uses this email address.")
            if phone and uow.users.exists_by_phone(phone):
                raise DuplicateResourceError("An account already uses this phone number.")
            role = uow.roles.get_by_name(RoleName.USER)
            if role is None:
                raise ResourceNotFoundError("Default roles are not initialized.")
            user = User(
                first_name=values["first_name"].strip(),
                last_name=values["last_name"].strip(),
                email=email,
                phone=phone,
                password_hash=self._password_hasher.hash(password),
                status=UserStatus.ACTIVE,
                preferred_locale=values.get("preferred_locale", "fa"),
                token_version=0,
            )
            uow.users.add(user)
            uow.flush()
            uow.roles.assign_to_user(user, role)
            uow.commit()
            return user.safe_dict([RoleName.USER.value])

    def login(
        self, identifier: str, password: str, client: ClientContext | None = None
    ) -> dict[str, Any]:
        normalized = normalize_destination(identifier)
        with self._uow_factory() as uow:
            user = (
                uow.users.get_by_email(normalized)
                if "@" in normalized
                else uow.users.get_by_phone(normalized)
            )
            if user is None or not self._password_hasher.verify(user.password_hash, password):
                raise AuthenticationError("Invalid credentials.")
            self._ensure_authenticatable(user)
            user.last_login_at = self._clock.now()
            roles = [role.name.value for role in uow.roles.list_by_user_id(user.id)]
            result = self._issue_session(uow, user, roles, client or ClientContext())
            uow.commit()
            return result

    def login_with_otp(
        self, destination: str, client: ClientContext | None = None
    ) -> dict[str, Any]:
        normalized = normalize_destination(destination)
        with self._uow_factory() as uow:
            user = (
                uow.users.get_by_email(normalized)
                if "@" in normalized
                else uow.users.get_by_phone(normalized)
            )
            if user is None:
                raise AuthenticationError("Unable to authenticate with this code.")
            self._ensure_authenticatable(user)
            if "@" in normalized and user.email_verified_at is None:
                user.email_verified_at = self._clock.now()
            if "@" not in normalized and user.phone_verified_at is None:
                user.phone_verified_at = self._clock.now()
            user.last_login_at = self._clock.now()
            roles = [role.name.value for role in uow.roles.list_by_user_id(user.id)]
            result = self._issue_session(uow, user, roles, client or ClientContext())
            uow.commit()
            return result

    def refresh_session(
        self, raw_refresh_token: str, client: ClientContext | None = None
    ) -> dict[str, Any]:
        claims = self._tokens.decode(raw_refresh_token, expected_type="refresh")
        jti = str(claims["jti"])
        now = self._clock.now()
        context = client or ClientContext()
        with self._uow_factory() as uow:
            record = uow.refresh_tokens.get_by_jti(jti)
            if record is None:
                raise TokenError("Refresh session was not found.")
            user = uow.users.get_by_id(record.user_id)
            if record.revoked_at is not None:
                uow.refresh_tokens.revoke_family(record.token_family, now)
                if user is not None:
                    user.token_version += 1
                uow.commit()
                raise TokenReuseDetected("Refresh token reuse detected; all sessions were revoked.")
            if not self._tokens.verify_token_hash(raw_refresh_token, record.token_hash):
                raise TokenError("Invalid refresh token.")
            if record.expires_at <= now:
                raise TokenError("Refresh token has expired.")
            if user is None:
                raise AuthenticationError("User is unavailable.")
            self._ensure_authenticatable(user)
            if int(claims["token_version"]) != user.token_version:
                raise TokenError("Refresh session is no longer valid.")
            if str(claims["sub"]) != user.public_id or str(claims["family"]) != record.token_family:
                raise TokenError("Refresh token claims do not match the session.")
            roles = [role.name.value for role in uow.roles.list_by_user_id(user.id)]
            access = self._tokens.create_access_token(user.public_id, roles, user.token_version)
            replacement = self._tokens.create_refresh_token(
                user.public_id, user.token_version, family=record.token_family
            )
            replacement_record = self._refresh_record(user, replacement, context)
            uow.refresh_tokens.revoke(
                record, now, replaced_by_jti=str(replacement.claims["jti"])
            )
            record.last_used_ip = context.ip_address
            uow.refresh_tokens.add(replacement_record)
            uow.commit()
            return self._session_result(user, roles, access, replacement)

    def logout(self, raw_refresh_token: str | None) -> None:
        if not raw_refresh_token:
            return
        try:
            claims = self._tokens.decode(raw_refresh_token, expected_type="refresh")
        except TokenError:
            return
        with self._uow_factory() as uow:
            record = uow.refresh_tokens.get_by_jti(str(claims["jti"]))
            if record is not None and record.revoked_at is None:
                uow.refresh_tokens.revoke(record, self._clock.now())
                uow.commit()

    def logout_all(self, user_public_id: str) -> None:
        with self._uow_factory() as uow:
            user = uow.users.get_by_public_id(user_public_id)
            if user is None:
                raise AuthenticationError("User is unavailable.")
            user.token_version += 1
            uow.refresh_tokens.revoke_all_for_user(user.id, self._clock.now())
            uow.commit()

    def authenticate_access_token(self, raw_access_token: str) -> AuthContext:
        claims = self._tokens.decode(raw_access_token, expected_type="access")
        with self._uow_factory() as uow:
            user = uow.users.get_by_public_id(str(claims["sub"]))
            if user is None:
                raise AuthenticationError("User is unavailable.")
            self._ensure_authenticatable(user)
            if int(claims["token_version"]) != user.token_version:
                raise TokenError("Access token is no longer valid.")
            roles = tuple(role.name.value for role in uow.roles.list_by_user_id(user.id))
            return AuthContext(user.public_id, roles, user.token_version)

    def get_current_user(self, user_public_id: str) -> dict[str, Any]:
        with self._uow_factory() as uow:
            user = uow.users.get_by_public_id(user_public_id)
            if user is None:
                raise AuthenticationError("User is unavailable.")
            self._ensure_authenticatable(user)
            roles = [role.name.value for role in uow.roles.list_by_user_id(user.id)]
            return user.safe_dict(roles)

    def change_password(
        self, user_public_id: str, current_password: str, new_password: str
    ) -> None:
        self._validate_password(new_password)
        with self._uow_factory() as uow:
            user = uow.users.get_by_public_id(user_public_id)
            if user is None:
                raise AuthenticationError("User is unavailable.")
            if not self._password_hasher.verify(user.password_hash, current_password):
                raise AuthenticationError("Current password is incorrect.")
            user.password_hash = self._password_hasher.hash(new_password)
            user.token_version += 1
            uow.refresh_tokens.revoke_all_for_user(user.id, self._clock.now())
            uow.commit()

    def create_default_roles(self) -> list[str]:
        with self._uow_factory() as uow:
            roles = uow.roles.create_default_roles()
            uow.commit()
            return [role.name.value for role in roles]

    def create_admin(self, values: dict[str, Any]) -> dict[str, Any]:
        email = self._normalize_email(values.get("email"))
        phone = self._normalize_phone(values.get("phone"))
        password = str(values.get("password") or "")
        with self._uow_factory() as uow:
            uow.roles.create_default_roles()
            user = uow.users.get_by_email(email) if email else None
            if user is None:
                self._validate_password(password)
                user = User(
                    first_name=values["first_name"].strip(),
                    last_name=values["last_name"].strip(),
                    email=email,
                    phone=phone,
                    password_hash=self._password_hasher.hash(password),
                    status=UserStatus.ACTIVE,
                    preferred_locale=values.get("preferred_locale", "fa"),
                    token_version=0,
                )
                uow.users.add(user)
                uow.flush()
            else:
                user.first_name = values["first_name"].strip()
                user.last_name = values["last_name"].strip()
                if phone is not None:
                    user.phone = phone
                if password:
                    self._validate_password(password)
                    user.password_hash = self._password_hasher.hash(password)
            admin_role = uow.roles.get_by_name(RoleName.ADMIN)
            if admin_role is None:
                raise ResourceNotFoundError("Admin role is unavailable.")
            uow.roles.assign_to_user(user, admin_role)
            uow.commit()
            roles = [role.name.value for role in uow.roles.list_by_user_id(user.id)]
            return user.safe_dict(roles)

    def _issue_session(
        self, uow: UnitOfWork, user: User, roles: list[str], client: ClientContext
    ) -> dict[str, Any]:
        access = self._tokens.create_access_token(user.public_id, roles, user.token_version)
        refresh = self._tokens.create_refresh_token(user.public_id, user.token_version)
        uow.refresh_tokens.add(self._refresh_record(user, refresh, client))
        return self._session_result(user, roles, access, refresh)

    def _refresh_record(
        self, user: User, refresh: EncodedToken, client: ClientContext
    ) -> RefreshToken:
        return RefreshToken(
            user_id=user.id,
            jti=str(refresh.claims["jti"]),
            token_family=str(refresh.claims["family"]),
            token_hash=self._tokens.hash_token(refresh.raw),
            issued_at=refresh.issued_at,
            expires_at=refresh.expires_at,
            created_by_ip=client.ip_address,
            user_agent=(client.user_agent or "")[:512] or None,
        )

    @staticmethod
    def _session_result(
        user: User,
        roles: list[str],
        access: EncodedToken,
        refresh: EncodedToken,
    ) -> dict[str, Any]:
        return {
            "access_token": access.raw,
            "access_token_expires_at": access.expires_at.isoformat(),
            "refresh_token": refresh.raw,
            "refresh_token_expires_at": refresh.expires_at.isoformat(),
            "user": user.safe_dict(roles),
        }

    def _validate_password(self, password: str) -> None:
        if len(password) < self._password_min_length:
            raise ValidationAppError(
                "Password does not meet the minimum length.",
                errors={"password": [f"Must be at least {self._password_min_length} characters."]},
            )

    @staticmethod
    def _ensure_authenticatable(user: User) -> None:
        if not user.is_authenticatable:
            raise AuthenticationError("Account is unavailable.")

    @staticmethod
    def _normalize_email(value: str | None) -> str | None:
        try:
            return normalize_email(value)
        except ValueError as exc:
            raise ValidationAppError(str(exc), errors={"email": [str(exc)]}) from exc

    @staticmethod
    def _normalize_phone(value: str | None) -> str | None:
        try:
            return normalize_phone(value)
        except ValueError as exc:
            raise ValidationAppError(str(exc), errors={"phone": [str(exc)]}) from exc
