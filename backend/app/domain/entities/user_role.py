from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.base import BIGINT, Base, CreatedAtMixin, IdMixin


class UserRole(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_role"),)

    user_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user = relationship("User", back_populates="role_links", overlaps="roles")
    role = relationship("Role", back_populates="user_links", overlaps="roles")
