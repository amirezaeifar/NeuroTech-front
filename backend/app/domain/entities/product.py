from __future__ import annotations

from datetime import date

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.base import (
    BIGINT,
    Base,
    IdMixin,
    MajorEntityMixin,
    PublicIdMixin,
    SoftDeleteMixin,
    TimestampMixin,
)
from app.domain.entities.enums import InquiryStatus, MediaType, ProductStatus, ReviewStatus, enum_type


class ProductCategory(MajorEntityMixin, Base):
    __tablename__ = "product_categories"

    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    translations = relationship(
        "ProductCategoryTranslation", back_populates="category", cascade="all, delete-orphan"
    )
    products = relationship("Product", back_populates="category")


class ProductCategoryTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "product_category_translations"
    __table_args__ = (
        UniqueConstraint("category_id", "locale", name="uq_product_category_translation_locale"),
    )

    category_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("product_categories.id", ondelete="CASCADE"), index=True
    )
    locale: Mapped[str] = mapped_column(String(10), index=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text())
    category = relationship("ProductCategory", back_populates="translations")


class Product(MajorEntityMixin, Base):
    __tablename__ = "products"
    __table_args__ = (Index("ix_products_category_status", "category_id", "status"),)

    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    sku: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)
    category_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("product_categories.id", ondelete="RESTRICT"), index=True
    )
    manufacturer: Mapped[str | None] = mapped_column(String(255))
    model_number: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[ProductStatus] = mapped_column(
        enum_type(ProductStatus), default=ProductStatus.DRAFT, index=True
    )
    is_featured: Mapped[bool] = mapped_column(default=False)
    is_published: Mapped[bool] = mapped_column(default=False, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    category = relationship("ProductCategory", back_populates="products")
    translations = relationship("ProductTranslation", back_populates="product", cascade="all, delete-orphan")
    media = relationship("ProductMedia", back_populates="product", cascade="all, delete-orphan")
    features = relationship("ProductFeature", back_populates="product", cascade="all, delete-orphan")
    specifications = relationship(
        "ProductSpecification", back_populates="product", cascade="all, delete-orphan"
    )


class ProductTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "product_translations"
    __table_args__ = (UniqueConstraint("product_id", "locale", name="uq_product_translation_locale"),)

    product_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    locale: Mapped[str] = mapped_column(String(10), index=True)
    name: Mapped[str] = mapped_column(String(255))
    short_description: Mapped[str | None] = mapped_column(Text())
    long_description: Mapped[str | None] = mapped_column(Text())
    inquiry_text: Mapped[str | None] = mapped_column(Text())
    product = relationship("Product", back_populates="translations")


class ProductMedia(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "product_media"
    __table_args__ = (Index("ix_product_media_order", "product_id", "position"),)

    product_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    media_type: Mapped[MediaType] = mapped_column(enum_type(MediaType))
    file_url: Mapped[str] = mapped_column(String(2048))
    alt_text: Mapped[str | None] = mapped_column(String(500))
    position: Mapped[int] = mapped_column(Integer, default=0)
    is_primary: Mapped[bool] = mapped_column(default=False)
    product = relationship("Product", back_populates="media")


class ProductFeature(IdMixin, TimestampMixin, Base):
    __tablename__ = "product_features"
    __table_args__ = (Index("ix_product_features_order", "product_id", "position"),)

    product_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0)
    product = relationship("Product", back_populates="features")
    translations = relationship(
        "ProductFeatureTranslation", back_populates="feature", cascade="all, delete-orphan"
    )


class ProductFeatureTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "product_feature_translations"
    __table_args__ = (UniqueConstraint("feature_id", "locale", name="uq_product_feature_translation_locale"),)

    feature_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("product_features.id", ondelete="CASCADE"), index=True
    )
    locale: Mapped[str] = mapped_column(String(10), index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text())
    feature = relationship("ProductFeature", back_populates="translations")


class ProductSpecification(IdMixin, TimestampMixin, Base):
    __tablename__ = "product_specifications"
    __table_args__ = (
        UniqueConstraint("product_id", "group_key", "spec_key", name="uq_product_spec_key"),
        Index("ix_product_spec_order", "product_id", "position"),
    )

    product_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    group_key: Mapped[str] = mapped_column(String(100))
    spec_key: Mapped[str] = mapped_column(String(100))
    spec_value: Mapped[str | None] = mapped_column(Text())
    unit: Mapped[str | None] = mapped_column(String(64))
    position: Mapped[int] = mapped_column(Integer, default=0)
    product = relationship("Product", back_populates="specifications")
    translations = relationship(
        "ProductSpecificationTranslation",
        back_populates="specification",
        cascade="all, delete-orphan",
    )


class ProductSpecificationTranslation(IdMixin, TimestampMixin, Base):
    __tablename__ = "product_specification_translations"
    __table_args__ = (
        UniqueConstraint("specification_id", "locale", name="uq_product_spec_translation_locale"),
    )

    specification_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("product_specifications.id", ondelete="CASCADE"), index=True
    )
    locale: Mapped[str] = mapped_column(String(10), index=True)
    group_label: Mapped[str | None] = mapped_column(String(255))
    key_label: Mapped[str | None] = mapped_column(String(255))
    value_label: Mapped[str | None] = mapped_column(Text())
    specification = relationship("ProductSpecification", back_populates="translations")


class ProductCertification(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "product_certifications"

    product_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("products.id", ondelete="RESTRICT"), index=True
    )
    name: Mapped[str] = mapped_column(String(255))
    certificate_number: Mapped[str | None] = mapped_column(String(120), index=True)
    issuer: Mapped[str | None] = mapped_column(String(255))
    issued_at: Mapped[date | None] = mapped_column(Date())
    expires_at: Mapped[date | None] = mapped_column(Date())
    document_url: Mapped[str | None] = mapped_column(String(2048))


class ProductClinicalTrial(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "product_clinical_trials"

    product_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("products.id", ondelete="RESTRICT"), index=True
    )
    title: Mapped[str] = mapped_column(String(500))
    organization: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str | None] = mapped_column(String(64), index=True)
    reference_url: Mapped[str | None] = mapped_column(String(2048))
    summary: Mapped[str | None] = mapped_column(Text())


class ProductReview(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "product_reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="product_review_rating_range"),
        Index("ix_product_reviews_product_status", "product_id", "status"),
    )

    product_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("products.id", ondelete="RESTRICT"), index=True
    )
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    rating: Mapped[int] = mapped_column(Integer)
    title: Mapped[str | None] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text())
    status: Mapped[ReviewStatus] = mapped_column(
        enum_type(ReviewStatus), default=ReviewStatus.PENDING, index=True
    )


class ProductInquiry(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "product_inquiries"

    product_id: Mapped[int] = mapped_column(
        BIGINT, ForeignKey("products.id", ondelete="RESTRICT"), index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        BIGINT, ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str | None] = mapped_column(String(320), index=True)
    phone: Mapped[str | None] = mapped_column(String(32), index=True)
    company: Mapped[str | None] = mapped_column(String(255))
    country: Mapped[str | None] = mapped_column(String(100))
    message: Mapped[str] = mapped_column(Text())
    status: Mapped[InquiryStatus] = mapped_column(
        enum_type(InquiryStatus), default=InquiryStatus.NEW, index=True
    )
    assigned_to: Mapped[int | None] = mapped_column(
        BIGINT, ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
