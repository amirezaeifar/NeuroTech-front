from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import MONEY_PRECISION, MONEY_SCALE
from app.domain.entities.base import BIGINT, Base, IdMixin, PublicIdMixin, SoftDeleteMixin, TimestampMixin
from app.domain.entities.enums import OrderItemType, OrderStatus, PaymentStatus, enum_type


class Order(IdMixin, PublicIdMixin, TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="order_subtotal_nonnegative"),
        CheckConstraint("discount_amount >= 0", name="order_discount_nonnegative"),
        CheckConstraint("tax_amount >= 0", name="order_tax_nonnegative"),
        CheckConstraint("total_amount >= 0", name="order_total_nonnegative"),
        Index("ix_orders_user_status", "user_id", "status"),
    )

    order_number: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    status: Mapped[OrderStatus] = mapped_column(enum_type(OrderStatus), default=OrderStatus.PENDING, index=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(MONEY_PRECISION, MONEY_SCALE), default=Decimal("0.00"))
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(MONEY_PRECISION, MONEY_SCALE), default=Decimal("0.00"))
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(MONEY_PRECISION, MONEY_SCALE), default=Decimal("0.00"))
    total_amount: Mapped[Decimal] = mapped_column(Numeric(MONEY_PRECISION, MONEY_SCALE), default=Decimal("0.00"))
    billing_name: Mapped[str | None] = mapped_column(String(255))
    billing_email: Mapped[str | None] = mapped_column(String(320))
    billing_phone: Mapped[str | None] = mapped_column(String(32))
    paid_at: Mapped[datetime | None] = mapped_column(DateTime())
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime())
    items = relationship("OrderItem", back_populates="order")
    payments = relationship("PaymentTransaction", back_populates="order")


class OrderItem(IdMixin, PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="order_item_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="order_item_unit_price_nonnegative"),
        CheckConstraint("subtotal >= 0", name="order_item_subtotal_nonnegative"),
        CheckConstraint(
            "(item_type = 'course' AND course_id IS NOT NULL AND product_id IS NULL) OR "
            "(item_type = 'product' AND product_id IS NOT NULL AND course_id IS NULL)",
            name="order_item_target_matches_type",
        ),
    )

    order_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("orders.id", ondelete="RESTRICT"), index=True)
    item_type: Mapped[OrderItemType] = mapped_column(enum_type(OrderItemType), index=True)
    course_id: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("courses.id", ondelete="RESTRICT"), index=True)
    product_id: Mapped[int | None] = mapped_column(BIGINT, ForeignKey("products.id", ondelete="RESTRICT"), index=True)
    title_snapshot: Mapped[str] = mapped_column(String(500))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(MONEY_PRECISION, MONEY_SCALE))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(MONEY_PRECISION, MONEY_SCALE))
    order = relationship("Order", back_populates="items")


class PaymentTransaction(IdMixin, PublicIdMixin, TimestampMixin, Base):
    __tablename__ = "payment_transactions"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="payment_amount_nonnegative"),
        Index("ix_payment_order_status", "order_id", "status"),
    )

    order_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("orders.id", ondelete="RESTRICT"), index=True)
    provider: Mapped[str] = mapped_column(String(100))
    method: Mapped[str] = mapped_column(String(100))
    status: Mapped[PaymentStatus] = mapped_column(enum_type(PaymentStatus), default=PaymentStatus.PENDING, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(MONEY_PRECISION, MONEY_SCALE))
    currency: Mapped[str] = mapped_column(String(3))
    authority: Mapped[str | None] = mapped_column(String(255), index=True)
    reference_number: Mapped[str | None] = mapped_column(String(255), index=True)
    gateway_response: Mapped[dict | None] = mapped_column(JSON())
    failure_code: Mapped[str | None] = mapped_column(String(100))
    failure_message: Mapped[str | None] = mapped_column(Text())
    verified_at: Mapped[datetime | None] = mapped_column(DateTime())
    order = relationship("Order", back_populates="payments")
