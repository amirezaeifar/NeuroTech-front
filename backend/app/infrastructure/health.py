from redis import Redis
from sqlalchemy import Engine, text

from app.domain.ports.health_probe import HealthProbe


class SqlAlchemyHealthProbe(HealthProbe):
    name = "database"

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def check(self) -> None:
        with self._engine.connect() as connection:
            connection.execute(text("SELECT 1"))


class RedisHealthProbe(HealthProbe):
    name = "redis"

    def __init__(self, client: Redis) -> None:
        self._client = client

    def check(self) -> None:
        self._client.ping()
