from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.base import BIGINT, Base, IdMixin, MajorEntityMixin, PublicIdMixin, SoftDeleteMixin, TimestampMixin
from app.domain.entities.enums import InquiryStatus, TradeDocumentStatus, TradeGroupType, TradeServiceType, enum_type


class TradeRegion(MajorEntityMixin, Base):
    __tablename__ = "trade_regions"

    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    translations = relationship("TradeRegionTranslation", back_populates="region", cascade="all, delete-orphan")


class TradeRegionTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "trade_region_translations"
    __table_args__ = (UniqueConstraint("region_id", "locale", name="uq_trade_region_translation_locale"),)

    region_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("trade_regions.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    name: Mapped[str] = mapped_column(String(255))
    note: Mapped[str | None] = mapped_column(Text())
    region = relationship("TradeRegion", back_populates="translations")


class TradeCountry(MajorEntityMixin, Base):
    __tablename__ = "trade_countries"
    __table_args__ = (UniqueConstraint("region_id", "iso_code", name="uq_trade_country_region_iso"),)

    region_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("trade_regions.id", ondelete="RESTRICT"), index=True)
    iso_code: Mapped[str] = mapped_column(String(2), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    translations = relationship("TradeCountryTranslation", back_populates="country", cascade="all, delete-orphan")


class TradeCountryTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "trade_country_translations"
    __table_args__ = (UniqueConstraint("country_id", "locale", name="uq_trade_country_translation_locale"),)

    country_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("trade_countries.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text())
    country = relationship("TradeCountry", back_populates="translations")


class TradeService(MajorEntityMixin, Base):
    __tablename__ = "trade_services"

    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    service_type: Mapped[TradeServiceType] = mapped_column(enum_type(TradeServiceType), index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    translations = relationship("TradeServiceTranslation", back_populates="service", cascade="all, delete-orphan")


class TradeServiceTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "trade_service_translations"
    __table_args__ = (UniqueConstraint("service_id", "locale", name="uq_trade_service_translation_locale"),)

    service_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("trade_services.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    name: Mapped[str] = mapped_column(String(255))
    short_description: Mapped[str | None] = mapped_column(Text())
    description: Mapped[str | None] = mapped_column(Text())
    service = relationship("TradeService", back_populates="translations")


class TradeDocument(MajorEntityMixin, Base):
    __tablename__ = "trade_documents"
    __table_args__ = (
        Index("ix_trade_documents_status_period", "status", "reporting_period"),
        Index("ix_trade_documents_region_location", "region", "location"),
    )

    document_code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    document_type: Mapped[str] = mapped_column(String(100), index=True)
    partner_name: Mapped[str | None] = mapped_column(String(500))
    category: Mapped[str | None] = mapped_column(String(255), index=True)
    location: Mapped[str | None] = mapped_column(String(255), index=True)
    region: Mapped[str | None] = mapped_column(String(255), index=True)
    reporting_period: Mapped[str | None] = mapped_column(String(100), index=True)
    status: Mapped[TradeDocumentStatus] = mapped_column(
        enum_type(TradeDocumentStatus), default=TradeDocumentStatus.DRAFT, index=True
    )
    is_published: Mapped[bool] = mapped_column(default=False, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime())
    translations = relationship("TradeDocumentTranslation", back_populates="document", cascade="all, delete-orphan")
    groups = relationship("TradeDocumentGroup", back_populates="document", cascade="all, delete-orphan")


class TradeDocumentTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "trade_document_translations"
    __table_args__ = (UniqueConstraint("document_id", "locale", name="uq_trade_document_translation_locale"),)

    document_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("trade_documents.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str | None] = mapped_column(Text())
    document = relationship("TradeDocument", back_populates="translations")


class TradeDocumentGroup(IdMixin, PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "trade_document_groups"
    __table_args__ = (UniqueConstraint("document_id", "position", name="uq_trade_document_group_position"),)

    document_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("trade_documents.id", ondelete="CASCADE"), index=True)
    group_type: Mapped[TradeGroupType] = mapped_column(enum_type(TradeGroupType))
    position: Mapped[int] = mapped_column(Integer)
    document = relationship("TradeDocument", back_populates="groups")
    translations = relationship("TradeDocumentGroupTranslation", back_populates="group", cascade="all, delete-orphan")


class TradeDocumentGroupTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "trade_document_group_translations"
    __table_args__ = (UniqueConstraint("group_id", "locale", name="uq_trade_document_group_translation_locale"),)

    group_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("trade_document_groups.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    title: Mapped[str] = mapped_column(String(500))
    body: Mapped[str | None] = mapped_column(Text())
    group = relationship("TradeDocumentGroup", back_populates="translations")


class TradeDocumentListItem(IdMixin, TimestampMixin, Base):
    __tablename__ = "trade_document_list_items"
    __table_args__ = (UniqueConstraint("group_id", "position", name="uq_trade_document_list_item_position"),)

    group_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("trade_document_groups.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    translations = relationship("TradeDocumentListItemTranslation", back_populates="item", cascade="all, delete-orphan")


class TradeDocumentListItemTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "trade_document_list_item_translations"
    __table_args__ = (UniqueConstraint("item_id", "locale", name="uq_trade_document_list_item_translation_locale"),)

    item_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("trade_document_list_items.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    text: Mapped[str] = mapped_column(Text())
    item = relationship("TradeDocumentListItem", back_populates="translations")


class TradeDocumentPair(IdMixin, TimestampMixin, Base):
    __tablename__ = "trade_document_pairs"
    __table_args__ = (UniqueConstraint("group_id", "position", name="uq_trade_document_pair_position"),)

    group_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("trade_document_groups.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    translations = relationship("TradeDocumentPairTranslation", back_populates="pair", cascade="all, delete-orphan")


class TradeDocumentPairTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "trade_document_pair_translations"
    __table_args__ = (UniqueConstraint("pair_id", "locale", name="uq_trade_document_pair_translation_locale"),)

    pair_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("trade_document_pairs.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    label: Mapped[str] = mapped_column(String(500))
    value: Mapped[str] = mapped_column(Text())
    pair = relationship("TradeDocumentPair", back_populates="translations")


class MarketReport(MajorEntityMixin, Base):
    __tablename__ = "market_reports"

    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    reporting_period: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[TradeDocumentStatus] = mapped_column(
        enum_type(TradeDocumentStatus), default=TradeDocumentStatus.DRAFT, index=True
    )
    is_published: Mapped[bool] = mapped_column(default=False, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime())
    translations = relationship("MarketReportTranslation", back_populates="report", cascade="all, delete-orphan")
    sections = relationship("MarketReportSection", back_populates="report", cascade="all, delete-orphan")


class MarketReportTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "market_report_translations"
    __table_args__ = (UniqueConstraint("report_id", "locale", name="uq_market_report_translation_locale"),)

    report_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("market_reports.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str | None] = mapped_column(Text())
    outlook: Mapped[str | None] = mapped_column(Text())
    report = relationship("MarketReport", back_populates="translations")


class MarketReportSection(IdMixin, PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "market_report_sections"
    __table_args__ = (UniqueConstraint("report_id", "position", name="uq_market_report_section_position"),)

    report_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("market_reports.id", ondelete="CASCADE"), index=True)
    position: Mapped[int] = mapped_column(Integer)
    report = relationship("MarketReport", back_populates="sections")
    translations = relationship("MarketReportSectionTranslation", back_populates="section", cascade="all, delete-orphan")


class MarketReportSectionTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "market_report_section_translations"
    __table_args__ = (UniqueConstraint("section_id", "locale", name="uq_market_report_section_translation_locale"),)

    section_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("market_report_sections.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    title: Mapped[str] = mapped_column(String(500))
    body: Mapped[str | None] = mapped_column(Text())
    section = relationship("MarketReportSection", back_populates="translations")


class MarketReportItem(IdMixin, TimestampMixin, Base):
    __tablename__ = "market_report_items"
    __table_args__ = (UniqueConstraint("section_id", "position", name="uq_market_report_item_position"),)

    section_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("market_report_sections.id", ondelete="CASCADE"), index=True)
    metric_key: Mapped[str | None] = mapped_column(String(160), index=True)
    metric_value: Mapped[str | None] = mapped_column(String(500))
    position: Mapped[int] = mapped_column(Integer)
    translations = relationship("MarketReportItemTranslation", back_populates="item", cascade="all, delete-orphan")


class MarketReportItemTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "market_report_item_translations"
    __table_args__ = (UniqueConstraint("item_id", "locale", name="uq_market_report_item_translation_locale"),)

    item_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("market_report_items.id", ondelete="CASCADE"), index=True)
    locale: Mapped[str] = mapped_column(String(10), index=True)
    label: Mapped[str] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text())
    item = relationship("MarketReportItem", back_populates="translations")


class PartnershipApplication(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "partnership_applications"

    organization_name: Mapped[str] = mapped_column(String(500))
    contact_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(320), index=True)
    phone: Mapped[str | None] = mapped_column(String(32), index=True)
    country: Mapped[str | None] = mapped_column(String(100), index=True)
    website: Mapped[str | None] = mapped_column(String(2048))
    message: Mapped[str] = mapped_column(Text())
    status: Mapped[InquiryStatus] = mapped_column(
        enum_type(InquiryStatus), default=InquiryStatus.NEW, index=True
    )
    assigned_to: Mapped[int | None] = mapped_column(
        BIGINT, ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
