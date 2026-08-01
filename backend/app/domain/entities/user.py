from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.base import Base, MajorEntityMixin
from app.domain.entities.enums import UserStatus, enum_type


class User(MajorEntityMixin, Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("email IS NOT NULL OR phone IS NOT NULL", name="user_contact_required"),
        Index("ix_users_status_deleted", "status", "deleted_at"),
    )

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        enum_type(UserStatus), default=UserStatus.PENDING, nullable=False
    )
    preferred_locale: Mapped[str] = mapped_column(String(10), default="fa", nullable=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime())
    phone_verified_at: Mapped[datetime | None] = mapped_column(DateTime())
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime())
    token_version: Mapped[int] = mapped_column(default=0, nullable=False)

    roles = relationship(
        "Role", secondary="user_roles", lazy="selectin", viewonly=True, overlaps="user_links,role_links"
    )
    role_links = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", passive_deletes=True)

    @property
    def is_authenticatable(self) -> bool:
        return self.deleted_at is None and self.status == UserStatus.ACTIVE

    def safe_dict(self, role_names: list[str] | None = None) -> dict[str, object]:
        return {
            "public_id": self.public_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "status": self.status.value,
            "preferred_locale": self.preferred_locale,
            "roles": role_names if role_names is not None else [role.name.value for role in self.roles],
            "email_verified_at": self.email_verified_at.isoformat() if self.email_verified_at else None,
            "phone_verified_at": self.phone_verified_at.isoformat() if self.phone_verified_at else None,
            "created_at": self.created_at.isoformat(),
        }
