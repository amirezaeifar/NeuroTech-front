from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import MONEY_PRECISION, MONEY_SCALE
from app.domain.entities.base import BIGINT, Base, IdMixin, MajorEntityMixin, PublicIdMixin, SoftDeleteMixin, TimestampMixin
from app.domain.entities.enums import CommentStatus, CourseLevel, CourseTier, EnrollmentStatus, LessonProgressStatus, enum_type


class CourseCategory(MajorEntityMixin, Base):
    __tablename__ = "course_categories"

    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    translations = relationship("CourseCategoryTranslation", back_populates="category", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="category")


class CourseCategoryTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "course_category_translations"
    __table_args__ = (UniqueConstraint("category_id", "locale", name="uq_course_category_translation_locale"),)

    category_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("course_categories.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text())
    category = relationship("CourseCategory", back_populates="translations")


class Course(MajorEntityMixin, Base):
    __tablename__ = "courses"
    __table_args__ = (
        CheckConstraint("price >= 0", name="course_price_nonnegative"),
        Index("ix_courses_category_published", "category_id", "is_published"),
    )

    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    category_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("course_categories.id", ondelete="RESTRICT"), index=True)
    instructor_partner_id: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("partners.id", ondelete="SET NULL"), index=True)
    field: Mapped[str | None] = mapped_column(String(100), index=True)
    level: Mapped[CourseLevel] = mapped_column(enum_type(CourseLevel), default=CourseLevel.BEGINNER)
    tier: Mapped[CourseTier] = mapped_column(enum_type(CourseTier), default=CourseTier.FREE, index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(MONEY_PRECISION, MONEY_SCALE), default=Decimal("0.00"))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    estimated_lesson_count: Mapped[int] = mapped_column(Integer, default=0)
    cover_light_url: Mapped[str | None] = mapped_column(String(2048))
    cover_dark_url: Mapped[str | None] = mapped_column(String(2048))
    header_light_url: Mapped[str | None] = mapped_column(String(2048))
    header_dark_url: Mapped[str | None] = mapped_column(String(2048))
    is_published: Mapped[bool] = mapped_column(default=False, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime())
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    updated_by: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    category = relationship("CourseCategory", back_populates="courses")
    translations = relationship("CourseTranslation", back_populates="course", cascade="all, delete-orphan")
    modules = relationship("CourseModule", back_populates="course", cascade="all, delete-orphan")
    lessons = relationship("CourseLesson", back_populates="course")


class CourseTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "course_translations"
    __table_args__ = (UniqueConstraint("course_id", "locale", name="uq_course_translation_locale"),)

    course_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    title: Mapped[str] = mapped_column(String(500))
    short_description: Mapped[str | None] = mapped_column(Text())
    long_description: Mapped[str | None] = mapped_column(Text())
    level_label: Mapped[str | None] = mapped_column(String(100))
    duration_label: Mapped[str | None] = mapped_column(String(100))
    course = relationship("Course", back_populates="translations")


class CourseModule(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "course_modules"
    __table_args__ = (UniqueConstraint("course_id", "position", name="uq_course_module_position"),)

    course_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    is_published: Mapped[bool] = mapped_column(default=False)
    course = relationship("Course", back_populates="modules")
    translations = relationship("CourseModuleTranslation", back_populates="module", cascade="all, delete-orphan")
    lessons = relationship("CourseLesson", back_populates="module")


class CourseModuleTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "course_module_translations"
    __table_args__ = (UniqueConstraint("module_id", "locale", name="uq_course_module_translation_locale"),)

    module_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("course_modules.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text())
    module = relationship("CourseModule", back_populates="translations")


class CourseLesson(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "course_lessons"
    __table_args__ = (
        UniqueConstraint("module_id", "position", name="uq_course_lesson_position"),
        CheckConstraint("duration_seconds >= 0", name="course_lesson_duration_nonnegative"),
    )

    course_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    module_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("course_modules.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    video_url: Mapped[str | None] = mapped_column(String(2048))
    video_provider: Mapped[str | None] = mapped_column(String(100))
    is_preview: Mapped[bool] = mapped_column(default=False)
    is_published: Mapped[bool] = mapped_column(default=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime())
    course = relationship("Course", back_populates="lessons")
    module = relationship("CourseModule", back_populates="lessons")
    translations = relationship("CourseLessonTranslation", back_populates="lesson", cascade="all, delete-orphan")


class CourseLessonTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "course_lesson_translations"
    __table_args__ = (UniqueConstraint("lesson_id", "locale", name="uq_course_lesson_translation_locale"),)

    lesson_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("course_lessons.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text())
    transcript: Mapped[str | None] = mapped_column(Text())
    lesson = relationship("CourseLesson", back_populates="translations")


class CourseOutcome(IdMixin, TimestampMixin, Base):
    __tablename__ = "course_outcomes"
    __table_args__ = (UniqueConstraint("course_id", "position", name="uq_course_outcome_position"),)

    course_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    translations = relationship("CourseOutcomeTranslation", back_populates="outcome", cascade="all, delete-orphan")


class CourseOutcomeTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "course_outcome_translations"
    __table_args__ = (UniqueConstraint("outcome_id", "locale", name="uq_course_outcome_translation_locale"),)

    outcome_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("course_outcomes.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    text: Mapped[str] = mapped_column(Text())
    outcome = relationship("CourseOutcome", back_populates="translations")


class CourseResource(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "course_resources"

    course_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("course_lessons.id", ondelete="SET NULL"), index=True)
    name: Mapped[str] = mapped_column(String(500))
    resource_type: Mapped[str] = mapped_column(String(64))
    file_url: Mapped[str] = mapped_column(String(2048))
    mime_type: Mapped[str | None] = mapped_column(String(255))
    file_size: Mapped[int | None] = mapped_column(BIGINT)
    is_downloadable: Mapped[bool] = mapped_column(default=True)
    position: Mapped[int] = mapped_column(Integer, default=0)


class CourseEnrollment(IdMixin, PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "course_enrollments"
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_course_enrollment_user_course"),)

    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    course_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("courses.id", ondelete="RESTRICT"), index=True)
    order_item_id: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("order_items.id", ondelete="SET NULL"), index=True)
    status: Mapped[EnrollmentStatus] = mapped_column(enum_type(EnrollmentStatus), default=EnrollmentStatus.PENDING)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime())
    expires_at: Mapped[datetime | None] = mapped_column(DateTime())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime())


class UserLessonProgress(IdMixin, TimestampMixin, Base):
    __tablename__ = "user_lesson_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_lesson_progress_user_lesson"),
        CheckConstraint("progress_percent >= 0 AND progress_percent <= 100", name="lesson_progress_percent_range"),
        CheckConstraint("progress_seconds >= 0", name="lesson_progress_seconds_nonnegative"),
    )

    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("course_lessons.id", ondelete="CASCADE"), index=True)
    status: Mapped[LessonProgressStatus] = mapped_column(enum_type(LessonProgressStatus), default=LessonProgressStatus.NOT_STARTED)
    progress_seconds: Mapped[int] = mapped_column(Integer, default=0)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime())
    last_watched_at: Mapped[datetime | None] = mapped_column(DateTime())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime())


class CourseComment(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "course_comments"
    __table_args__ = (Index("ix_course_comments_course_status", "course_id", "status"),)

    course_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("courses.id", ondelete="RESTRICT"), index=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    parent_id: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("course_comments.id", ondelete="SET NULL"), index=True)
    body: Mapped[str] = mapped_column(Text())
    status: Mapped[CommentStatus] = mapped_column(enum_type(CommentStatus), default=CommentStatus.PENDING)
    is_instructor_answer: Mapped[bool] = mapped_column(default=False)
