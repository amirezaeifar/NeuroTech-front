from __future__ import annotations

from sqlalchemy import Engine, create_engine

from app.core.config import Settings


def create_database_engine(settings: Settings) -> Engine:
    options: dict[str, object] = {
        "pool_pre_ping": True,
        "echo": settings.db_echo,
        "future": True,
    }
    if not settings.database_url.startswith("sqlite"):
        options.update(
            {
                "pool_size": settings.db_pool_size,
                "max_overflow": settings.db_max_overflow,
                "pool_recycle": settings.db_pool_recycle_seconds,
            }
        )
    elif settings.database_url in {"sqlite://", "sqlite:///:memory:"}:
        from sqlalchemy.pool import StaticPool

        options.update(
            {
                "connect_args": {"check_same_thread": False},
                "poolclass": StaticPool,
            }
        )
    return create_engine(settings.database_url, **options)
