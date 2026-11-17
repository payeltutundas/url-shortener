"""Database connection. The engine is created lazily, so importing this file
does not open any connection."""
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Parent class for all database tables."""


@lru_cache
def get_engine():
    """Create the engine on first use (this does not connect yet)."""
    url = get_settings().database_url
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Check your .env file.")
    return create_engine(url, pool_pre_ping=True)


def create_tables():
    """Create all tables if they do not exist yet."""
    import app.models  # noqa: F401  (makes sure the models are registered)

    Base.metadata.create_all(get_engine())


def get_db():
    """FastAPI dependency: give each request its own database session."""
    session = sessionmaker(bind=get_engine(), expire_on_commit=False)()
    try:
        yield session
    finally:
        session.close()
