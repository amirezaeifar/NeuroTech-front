from __future__ import annotations

from sqlalchemy import ForeignKey, Index, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.entities.base import BIGINT, Base, IdMixin, PublicIdMixin, TimestampMixin
from app.domain.entities.enums import ModerationActionType, ModerationStatus, enum_type


class ModerationItem(IdMixin, PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "moderation_items"
    __table_args__ = (Index("ix_moderation_queue", "status", "subject_type"),)

    subject_type: Mapped[str] = mapped_column(String(100), index=True)
    subject_public_id: Mapped[str] = mapped_column(String(36), index=True)
    status: Mapped[ModerationStatus] = mapped_column(
        enum_type(ModerationStatus), default=ModerationStatus.PENDING, index=True
    )
    submitted_by: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    assigned_to: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    reason: Mapped[str | None] = mapped_column(Text())


class ModerationAction(IdMixin, TimestampMixin, Base):
    __tablename__ = "moderation_actions"

    moderation_item_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("moderation_items.id", ondelete="RESTRICT"), index=True
    )
    actor_id: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    action_type: Mapped[ModerationActionType] = mapped_column(enum_type(ModerationActionType), index=True)
    note: Mapped[str | None] = mapped_column(Text())


class AuditLog(IdMixin, TimestampMixin, Base):
    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_subject", "subject_type", "subject_public_id"),)

    actor_id: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    action: Mapped[str] = mapped_column(String(160), index=True)
    subject_type: Mapped[str] = mapped_column(String(100), index=True)
    subject_public_id: Mapped[str | None] = mapped_column(String(36), index=True)
    before_data: Mapped[dict | None] = mapped_column(JSON())
    after_data: Mapped[dict | None] = mapped_column(JSON())
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(512))
