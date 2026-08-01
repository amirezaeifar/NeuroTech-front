from sqlalchemy import Engine
from sqlalchemy.orm import scoped_session, sessionmaker


def create_session_registry(engine: Engine):
    factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    return scoped_session(factory)
