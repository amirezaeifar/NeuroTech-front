from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.base import BIGINT, Base, IdMixin, PublicIdMixin, SoftDeleteMixin, TimestampMixin
from app.domain.entities.enums import ContactMessageStatus, ContentStatus, ContentType, enum_type


class ContactMessage(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "contact_messages"

    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(320), index=True)
    phone: Mapped[str | None] = mapped_column(String(32), index=True)
    subject: Mapped[str] = mapped_column(String(500))
    message: Mapped[str] = mapped_column(Text())
    status: Mapped[ContactMessageStatus] = mapped_column(
        enum_type(ContactMessageStatus), default=ContactMessageStatus.NEW, index=True
    )
    assigned_to: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    admin_note: Mapped[str | None] = mapped_column(Text())


class ContentEntry(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "content_entries"
    __table_args__ = (Index("ix_content_entries_type_status", "content_type", "status"),)

    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    content_type: Mapped[ContentType] = mapped_column(enum_type(ContentType), index=True)
    status: Mapped[ContentStatus] = mapped_column(enum_type(ContentStatus), default=ContentStatus.DRAFT, index=True)
    publish_at: Mapped[datetime | None] = mapped_column(DateTime(), index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime())
    created_by: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    updated_by: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    translations = relationship("ContentEntryTranslation", back_populates="content_entry", cascade="all, delete-orphan")


class ContentEntryTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "content_entry_translations"
    __table_args__ = (UniqueConstraint("content_entry_id", "locale", name="uq_content_entry_translation_locale"),)

    content_entry_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("content_entries.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str | None] = mapped_column(Text())
    body: Mapped[str | None] = mapped_column(Text())
    content_entry = relationship("ContentEntry", back_populates="translations")


class SiteSetting(IdMixin, TimestampMixin, Base):
    __tablename__ = "site_settings"

    setting_key: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    setting_value: Mapped[dict | str | int | bool | None] = mapped_column(JSON())
    value_type: Mapped[str] = mapped_column(String(32))
    is_public: Mapped[bool] = mapped_column(default=False, index=True)
    updated_by: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="SET NULL"), index=True)
