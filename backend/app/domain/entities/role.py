from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.base import Base, IdMixin, TimestampMixin
from app.domain.entities.enums import RoleName, enum_type


class Role(IdMixin, TimestampMixin, Base):
    __tablename__ = "roles"

    name: Mapped[RoleName] = mapped_column(enum_type(RoleName), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text())
    user_links = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
