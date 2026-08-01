from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.base import BIGINT, Base, IdMixin, MajorEntityMixin, PublicIdMixin, SoftDeleteMixin, TimestampMixin
from app.domain.entities.enums import PartnerStatus, PartnerType, enum_type


class Partner(MajorEntityMixin, Base):
    __tablename__ = "partners"
    __table_args__ = (Index("ix_partners_type_status", "partner_type", "status"),)

    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    partner_type: Mapped[PartnerType] = mapped_column(enum_type(PartnerType), index=True)
    email: Mapped[str | None] = mapped_column(String(320), index=True)
    phone: Mapped[str | None] = mapped_column(String(32), index=True)
    website: Mapped[str | None] = mapped_column(String(2048))
    avatar_url: Mapped[str | None] = mapped_column(String(2048))
    cover_url: Mapped[str | None] = mapped_column(String(2048))
    status: Mapped[PartnerStatus] = mapped_column(
        enum_type(PartnerStatus), default=PartnerStatus.PENDING, index=True
    )
    is_featured: Mapped[bool] = mapped_column(default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    translations = relationship("PartnerTranslation", back_populates="partner", cascade="all, delete-orphan")
    experiences = relationship("PartnerExperience", back_populates="partner", cascade="all, delete-orphan")
    education = relationship("PartnerEducation", back_populates="partner", cascade="all, delete-orphan")


class PartnerTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "partner_translations"
    __table_args__ = (UniqueConstraint("partner_id", "locale", name="uq_partner_translation_locale"),)

    partner_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("partners.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    name: Mapped[str] = mapped_column(String(255))
    title: Mapped[str | None] = mapped_column(String(500))
    affiliation: Mapped[str | None] = mapped_column(String(500))
    qualification: Mapped[str | None] = mapped_column(String(500))
    bio: Mapped[str | None] = mapped_column(Text())
    methodology: Mapped[str | None] = mapped_column(Text())
    impact: Mapped[str | None] = mapped_column(Text())
    platform: Mapped[str | None] = mapped_column(String(255))
    status_label: Mapped[str | None] = mapped_column(String(100))
    partner = relationship("Partner", back_populates="translations")


class PartnerExperience(IdMixin, TimestampMixin, Base):
    __tablename__ = "partner_experiences"
    __table_args__ = (Index("ix_partner_experiences_order", "partner_id", "position"),)

    partner_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("partners.id", ondelete="CASCADE"), index=True)
    organization: Mapped[str | None] = mapped_column(String(500))
    start_date: Mapped[date | None] = mapped_column(Date())
    end_date: Mapped[date | None] = mapped_column(Date())
    position: Mapped[int] = mapped_column(Integer, default=0)
    partner = relationship("Partner", back_populates="experiences")
    translations = relationship("PartnerExperienceTranslation", back_populates="experience", cascade="all, delete-orphan")


class PartnerExperienceTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "partner_experience_translations"
    __table_args__ = (UniqueConstraint("experience_id", "locale", name="uq_partner_experience_translation_locale"),)

    experience_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("partner_experiences.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    role: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text())
    experience = relationship("PartnerExperience", back_populates="translations")


class PartnerEducation(IdMixin, TimestampMixin, Base):
    __tablename__ = "partner_education"
    __table_args__ = (Index("ix_partner_education_order", "partner_id", "position"),)

    partner_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("partners.id", ondelete="CASCADE"), index=True)
    institution: Mapped[str | None] = mapped_column(String(500))
    year: Mapped[int | None] = mapped_column(Integer)
    position: Mapped[int] = mapped_column(Integer, default=0)
    partner = relationship("Partner", back_populates="education")
    translations = relationship("PartnerEducationTranslation", back_populates="education", cascade="all, delete-orphan")


class PartnerEducationTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "partner_education_translations"
    __table_args__ = (UniqueConstraint("education_id", "locale", name="uq_partner_education_translation_locale"),)

    education_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("partner_education.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    degree: Mapped[str] = mapped_column(String(500))
    field: Mapped[str | None] = mapped_column(String(500))
    education = relationship("PartnerEducation", back_populates="translations")


class PartnerPublication(IdMixin, PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "partner_publications"

    partner_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("partners.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(1000))
    publication: Mapped[str | None] = mapped_column(String(500))
    published_year: Mapped[int | None] = mapped_column(Integer, index=True)
    url: Mapped[str | None] = mapped_column(String(2048))
    doi: Mapped[str | None] = mapped_column(String(255), index=True)


class PartnerExpertise(IdMixin, TimestampMixin, Base):
    __tablename__ = "partner_expertise"
    __table_args__ = (
        UniqueConstraint("partner_id", "expertise_key", name="uq_partner_expertise_key"),
        Index("ix_partner_expertise_order", "partner_id", "position"),
    )

    partner_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("partners.id", ondelete="CASCADE"), index=True)
    expertise_key: Mapped[str] = mapped_column(String(160))
    position: Mapped[int] = mapped_column(Integer, default=0)
    translations = relationship("PartnerExpertiseTranslation", back_populates="expertise", cascade="all, delete-orphan")


class PartnerExpertiseTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "partner_expertise_translations"
    __table_args__ = (UniqueConstraint("expertise_id", "locale", name="uq_partner_expertise_translation_locale"),)

    expertise_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("partner_expertise.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text())
    expertise = relationship("PartnerExpertise", back_populates="translations")


class PartnerPlaylist(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "partner_playlists"

    partner_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("partners.id", ondelete="CASCADE"), index=True)
    lesson_count: Mapped[int] = mapped_column(Integer, default=0)
    position: Mapped[int] = mapped_column(Integer, default=0)
    translations = relationship("PartnerPlaylistTranslation", back_populates="playlist", cascade="all, delete-orphan")


class PartnerPlaylistTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "partner_playlist_translations"
    __table_args__ = (UniqueConstraint("playlist_id", "locale", name="uq_partner_playlist_translation_locale"),)

    playlist_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("partner_playlists.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text())
    playlist = relationship("PartnerPlaylist", back_populates="translations")


class PartnerCourse(IdMixin, TimestampMixin, Base):
    __tablename__ = "partner_courses"
    __table_args__ = (UniqueConstraint("partner_id", "course_id", name="uq_partner_course"),)

    partner_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("partners.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(100), default="instructor")
