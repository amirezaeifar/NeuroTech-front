from __future__ import annotations

import hashlib
import os
import time
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from alembic import command
from alembic.config import Config
from redis import Redis
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.domain.entities import Base
from app.domain.entities.academy import Course, CourseCategory, CourseCategoryTranslation
from app.domain.entities.commerce import Order, OrderItem
from app.domain.entities.enums import (
    CourseLevel,
    CourseTier,
    EventStatus,
    EventType,
    OrderItemType,
    OrderStatus,
    PartnerStatus,
    PartnerType,
    ProductStatus,
    RoleName,
    TradeDocumentStatus,
    UserStatus,
)
from app.domain.entities.event import Event
from app.domain.entities.partner import Partner
from app.domain.entities.product import Product, ProductCategory, ProductTranslation
from app.domain.entities.refresh_token import RefreshToken
from app.domain.entities.role import Role
from app.domain.entities.trade import TradeDocument, TradeDocumentTranslation
from app.domain.entities.user import User
from app.domain.entities.user_role import UserRole
from app.domain.ports.otp_store import OtpRecord, OtpVerificationStatus
from app.infrastructure.db.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.redis.otp_store import RedisOtpStore

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def integration_resources():
    database_url = os.getenv("INTEGRATION_DATABASE_URL", "")
    redis_url = os.getenv("INTEGRATION_REDIS_URL", "")
    if not database_url.startswith("mysql+mysqlconnector://") or not redis_url:
        pytest.skip(
            "Set a dedicated mysql+mysqlconnector INTEGRATION_DATABASE_URL and INTEGRATION_REDIS_URL."
        )
    engine = create_engine(database_url, pool_pre_ping=True)
    redis_client = Redis.from_url(redis_url, decode_responses=True)
    previous_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = database_url
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    try:
        yield engine, Session, redis_client
    finally:
        integration_keys = list(redis_client.scan_iter("neurotech:integration*"))
        if integration_keys:
            redis_client.delete(*integration_keys)
        command.downgrade(config, "base")
        engine.dispose()
        if previous_url is None:
            os.environ.pop("DATABASE_URL", None)
        else:
            os.environ["DATABASE_URL"] = previous_url


def _user(email: str, phone: str | None = None) -> User:
    return User(
        first_name="Integration",
        last_name="User",
        email=email,
        phone=phone,
        password_hash="not-a-real-login-hash",
        status=UserStatus.ACTIVE,
        preferred_locale="en",
        token_version=0,
    )


def test_alembic_upgrade_created_complete_schema(integration_resources):
    engine, _, redis_client = integration_resources
    assert redis_client.ping()
    names = set(inspect(engine).get_table_names())
    assert len(names) == 88
    assert {"users", "products", "courses", "events", "partners", "orders", "alembic_version"} <= names


def test_sqlalchemy_uow_commit_and_rollback(integration_resources):
    _, Session, _ = integration_resources
    email = f"uow-{time.time_ns()}@example.com"
    with SqlAlchemyUnitOfWork(Session) as uow:
        uow.roles.create_default_roles()
        user = _user(email)
        uow.users.add(user)
        uow.flush()
        role = uow.roles.get_by_name(RoleName.USER)
        uow.roles.assign_to_user(user, role)
        uow.commit()
    with Session() as session:
        assert session.scalar(select(User).where(User.email == email)) is not None

    rollback_email = f"rollback-{time.time_ns()}@example.com"
    with pytest.raises(RuntimeError):
        with SqlAlchemyUnitOfWork(Session) as uow:
            uow.users.add(_user(rollback_email))
            uow.flush()
            raise RuntimeError("force rollback")
    with Session() as session:
        assert session.scalar(select(User).where(User.email == rollback_email)) is None


def test_unique_user_role_and_translation_constraints(integration_resources):
    _, Session, _ = integration_resources
    email = f"unique-{time.time_ns()}@example.com"
    phone = f"+989{str(time.time_ns())[-9:]}"
    with Session.begin() as session:
        user = _user(email, phone)
        role = session.scalar(select(Role).where(Role.name == RoleName.USER))
        session.add(user)
        session.flush()
        session.add(UserRole(user_id=user.id, role_id=role.id))
        category = CourseCategory(slug=f"category-{time.time_ns()}")
        session.add(category)
        session.flush()
        session.add(CourseCategoryTranslation(category_id=category.id, locale="en", name="Neurology"))

    with Session() as session:
        session.add(_user(email))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        session.add(_user(f"other-{time.time_ns()}@example.com", phone))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        persisted_user = session.scalar(select(User).where(User.email == email))
        role = session.scalar(select(Role).where(Role.name == RoleName.USER))
        session.add(UserRole(user_id=persisted_user.id, role_id=role.id))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        category = session.scalar(
            select(CourseCategory).where(CourseCategory.slug.like("category-%"))
        )
        session.add(CourseCategoryTranslation(category_id=category.id, locale="en", name="Duplicate"))
        with pytest.raises(IntegrityError):
            session.commit()


def test_core_business_relationships_and_decimal_money(integration_resources):
    _, Session, _ = integration_resources
    suffix = str(time.time_ns())
    with Session.begin() as session:
        user = _user(f"relations-{suffix}@example.com")
        partner = Partner(
            slug=f"partner-{suffix}",
            partner_type=PartnerType.SPECIALIST,
            status=PartnerStatus.ACTIVE,
        )
        product_category = ProductCategory(slug=f"devices-{suffix}")
        course_category = CourseCategory(slug=f"courses-{suffix}")
        session.add_all([user, partner, product_category, course_category])
        session.flush()
        product = Product(
            slug=f"product-{suffix}",
            sku=f"SKU-{suffix}",
            category_id=product_category.id,
            status=ProductStatus.ACTIVE,
        )
        course = Course(
            slug=f"course-{suffix}",
            code=f"CLN-{suffix[-8:]}",
            category_id=course_category.id,
            instructor_partner_id=partner.id,
            level=CourseLevel.INTERMEDIATE,
            tier=CourseTier.PREMIUM,
            price=Decimal("129.00"),
            currency="USD",
        )
        event = Event(
            slug=f"event-{suffix}",
            event_type=EventType.ONLINE,
            status=EventStatus.SCHEDULED,
            start_at=datetime.utcnow(),
        )
        trade = TradeDocument(
            document_code=f"DOC-{suffix}",
            document_type="technical",
            status=TradeDocumentStatus.PUBLISHED,
        )
        session.add_all([product, course, event, trade])
        session.flush()
        session.add_all(
            [
                ProductTranslation(product_id=product.id, locale="en", name="Neural Device"),
                TradeDocumentTranslation(document_id=trade.id, locale="en", title="Market Document"),
            ]
        )
        order = Order(
            order_number=f"ORD-{suffix}",
            user_id=user.id,
            status=OrderStatus.PENDING,
            currency="USD",
            subtotal=Decimal("129.00"),
            discount_amount=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("129.00"),
        )
        session.add(order)
        session.flush()
        session.add(
            OrderItem(
                order_id=order.id,
                item_type=OrderItemType.COURSE,
                course_id=course.id,
                product_id=None,
                title_snapshot="Clinical Neurology",
                unit_price=Decimal("129.00"),
                quantity=1,
                subtotal=Decimal("129.00"),
            )
        )
    with Session() as session:
        persisted = session.scalar(select(Order).where(Order.order_number == f"ORD-{suffix}"))
        assert persisted.total_amount == Decimal("129.00")
        assert len(persisted.items) == 1


def test_refresh_token_family_persistence_and_revocation(integration_resources):
    _, Session, _ = integration_resources
    now = datetime.utcnow()
    with SqlAlchemyUnitOfWork(Session) as uow:
        user = _user(f"refresh-{time.time_ns()}@example.com")
        uow.users.add(user)
        uow.flush()
        family = f"family-{time.time_ns()}"
        for index in range(2):
            uow.refresh_tokens.add(
                RefreshToken(
                    user_id=user.id,
                    jti=f"jti-{time.time_ns()}-{index}",
                    token_family=family,
                    token_hash=hashlib.sha256(str(index).encode()).hexdigest(),
                    issued_at=now,
                    expires_at=now + timedelta(days=1),
                )
            )
        uow.commit()
    with SqlAlchemyUnitOfWork(Session) as uow:
        assert len(uow.refresh_tokens.list_active_for_user(user.id, now)) == 2
        assert uow.refresh_tokens.revoke_family(family, now) == 2
        uow.commit()


def test_redis_otp_ttl_attempts_and_single_use(integration_resources):
    _, _, redis_client = integration_resources
    store = RedisOtpStore(redis_client, namespace="neurotech:integration")
    now = datetime.utcnow()
    destination = f"+989{str(time.time_ns())[-9:]}"
    record = OtpRecord(
        purpose="login",
        destination=destination,
        code_hash="expected-hash",
        created_at=now,
        expires_at=now + timedelta(seconds=30),
        attempt_count=0,
        max_attempts=3,
        request_count=1,
        resend_available_at=now + timedelta(seconds=10),
    )
    store.create(record, ttl_seconds=30, max_requests_per_hour=5)
    key = f"neurotech:integration:otp:login:{destination}"
    assert 0 < redis_client.ttl(key) <= 30
    assert (
        store.verify_and_consume("login", destination, "expected-hash")
        is OtpVerificationStatus.VERIFIED
    )
    assert (
        store.verify_and_consume("login", destination, "expected-hash")
        is OtpVerificationStatus.MISSING
    )
