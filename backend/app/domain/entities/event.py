from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.base import BIGINT, Base, CreatedAtMixin, IdMixin, PublicIdMixin, SoftDeleteMixin, TimestampMixin
from app.domain.entities.enums import AttendanceStatus, CommentStatus, EventRegistrationStatus, EventStatus, EventType, MediaType, ModerationStatus, enum_type


class Event(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint("end_at IS NULL OR end_at >= start_at", name="event_end_after_start"),
        CheckConstraint("capacity IS NULL OR capacity >= 0", name="event_capacity_nonnegative"),
        CheckConstraint(
            "registration_closes_at IS NULL OR registration_opens_at IS NULL OR registration_closes_at >= registration_opens_at",
            name="event_registration_window",
        ),
        Index("ix_events_status_start", "status", "start_at"),
    )

    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    event_type: Mapped[EventType] = mapped_column(enum_type(EventType), index=True)
    status: Mapped[EventStatus] = mapped_column(enum_type(EventStatus), default=EventStatus.DRAFT, index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(), index=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime())
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    capacity: Mapped[int | None] = mapped_column(Integer)
    registration_opens_at: Mapped[datetime | None] = mapped_column(DateTime())
    registration_closes_at: Mapped[datetime | None] = mapped_column(DateTime())
    is_registration_required: Mapped[bool] = mapped_column(default=True)
    venue_name: Mapped[str | None] = mapped_column(String(500))
    venue_address: Mapped[str | None] = mapped_column(Text())
    stream_url: Mapped[str | None] = mapped_column(String(2048))
    recording_url: Mapped[str | None] = mapped_column(String(2048))
    cover_url: Mapped[str | None] = mapped_column(String(2048))
    is_published: Mapped[bool] = mapped_column(default=False, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime())
    translations = relationship("EventTranslation", back_populates="event", cascade="all, delete-orphan")
    sessions = relationship("EventSession", back_populates="event", cascade="all, delete-orphan")
    registrations = relationship("EventRegistration", back_populates="event")


class EventTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "event_translations"
    __table_args__ = (UniqueConstraint("event_id", "locale", name="uq_event_translation_locale"),)

    event_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("events.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str | None] = mapped_column(Text())
    description: Mapped[str | None] = mapped_column(Text())
    tag: Mapped[str | None] = mapped_column(String(100))
    venue_description: Mapped[str | None] = mapped_column(Text())
    event = relationship("Event", back_populates="translations")


class EventSession(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "event_sessions"
    __table_args__ = (
        CheckConstraint("end_at IS NULL OR end_at >= start_at", name="event_session_end_after_start"),
        Index("ix_event_sessions_order", "event_id", "position"),
    )

    event_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("events.id", ondelete="CASCADE"), index=True)
    speaker_partner_id: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("partners.id", ondelete="SET NULL"), index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime())
    end_at: Mapped[datetime | None] = mapped_column(DateTime())
    position: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[EventStatus] = mapped_column(enum_type(EventStatus), default=EventStatus.SCHEDULED)
    event = relationship("Event", back_populates="sessions")
    translations = relationship("EventSessionTranslation", back_populates="session", cascade="all, delete-orphan")


class EventSessionTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "event_session_translations"
    __table_args__ = (UniqueConstraint("session_id", "locale", name="uq_event_session_translation_locale"),)

    session_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("event_sessions.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text())
    session = relationship("EventSession", back_populates="translations")


class EventSpeaker(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "event_speakers"
    __table_args__ = (
        UniqueConstraint("event_id", "partner_id", "role", name="uq_event_speaker_role"),
        Index("ix_event_speakers_order", "event_id", "position"),
    )

    event_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("events.id", ondelete="CASCADE"), index=True)
    partner_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("partners.id", ondelete="RESTRICT"), index=True)
    role: Mapped[str] = mapped_column(String(100))
    position: Mapped[int] = mapped_column(Integer, default=0)


class EventRegistration(IdMixin, PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "event_registrations"
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="uq_event_registration_user"),)

    event_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("events.id", ondelete="RESTRICT"), index=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    status: Mapped[EventRegistrationStatus] = mapped_column(
        enum_type(EventRegistrationStatus), default=EventRegistrationStatus.PENDING, index=True
    )
    registered_at: Mapped[datetime] = mapped_column(DateTime())
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime())
    checked_in_at: Mapped[datetime | None] = mapped_column(DateTime())
    attendance_status: Mapped[AttendanceStatus] = mapped_column(
        enum_type(AttendanceStatus), default=AttendanceStatus.UNKNOWN
    )
    event = relationship("Event", back_populates="registrations")


class EventResource(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "event_resources"

    event_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("events.id", ondelete="CASCADE"), index=True)
    session_id: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("event_sessions.id", ondelete="SET NULL"), index=True)
    name: Mapped[str] = mapped_column(String(500))
    resource_type: Mapped[str] = mapped_column(String(64))
    file_url: Mapped[str] = mapped_column(String(2048))
    mime_type: Mapped[str | None] = mapped_column(String(255))
    file_size: Mapped[int | None] = mapped_column(BIGINT)
    position: Mapped[int] = mapped_column(Integer, default=0)


class EventMedia(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "event_media"

    event_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("events.id", ondelete="CASCADE"), index=True)
    media_type: Mapped[MediaType] = mapped_column(enum_type(MediaType))
    file_url: Mapped[str] = mapped_column(String(2048))
    caption: Mapped[str | None] = mapped_column(String(1000))
    position: Mapped[int] = mapped_column(Integer, default=0)


class EventMessage(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "event_messages"
    __table_args__ = (Index("ix_event_messages_timeline", "event_id", "created_at"),)

    event_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("events.id", ondelete="RESTRICT"), index=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    body: Mapped[str] = mapped_column(Text())
    status: Mapped[ModerationStatus] = mapped_column(
        enum_type(ModerationStatus), default=ModerationStatus.PENDING
    )


class EventQuestion(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "event_questions"

    event_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("events.id", ondelete="RESTRICT"), index=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    body: Mapped[str] = mapped_column(Text())
    answer: Mapped[str | None] = mapped_column(Text())
    answered_by: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime())
    status: Mapped[ModerationStatus] = mapped_column(
        enum_type(ModerationStatus), default=ModerationStatus.PENDING
    )


class EventQuestionVote(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "event_question_votes"
    __table_args__ = (UniqueConstraint("question_id", "user_id", name="uq_event_question_vote_user"),)

    question_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("event_questions.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"), index=True)


class EventComment(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "event_comments"

    event_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("events.id", ondelete="RESTRICT"), index=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    parent_id: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("event_comments.id", ondelete="SET NULL"), index=True)
    body: Mapped[str] = mapped_column(Text())
    status: Mapped[CommentStatus] = mapped_column(
        enum_type(CommentStatus), default=CommentStatus.PENDING, index=True
    )
