"""Shared test setup. Uses ONLY the test database (TEST_DATABASE_URL)."""
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.database import Base, get_db
from app.main import app
from app.models import Link


@pytest.fixture(scope="session")
def engine():
    url = get_settings().test_database_url
    assert url, "TEST_DATABASE_URL is not set"
    name = make_url(url).database
    assert name == "urlshortener_test", f"Refusing to run tests on database {name!r}"
    assert name != make_url(get_settings().database_url).database
    eng = create_engine(url, pool_pre_ping=True)
    yield eng
    eng.dispose()


@pytest.fixture(autouse=True)
def db_tables(engine):
    """Fresh tables before each test, dropped after."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture
def client(session_factory):
    def override_get_db():
        s = session_factory()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db
    # No "with": the startup hook (which uses the real DB) is not run.
    c = TestClient(app, follow_redirects=False)
    yield c
    app.dependency_overrides.clear()


@pytest.fixture
def base_url():
    return get_settings().base_url.rstrip("/")


@pytest.fixture
def make_link(session_factory):
    """Insert a link straight into the test DB (e.g. already expired)."""

    def _make(code="oldlink", url="https://example.com/old", expires_at=None, clicks=0):
        with session_factory() as s:
            s.add(Link(code=code, original_url=url, expires_at=expires_at, clicks=clicks))
            s.commit()

    return _make


@pytest.fixture
def get_clicks(session_factory):
    def _get(code):
        with session_factory() as s:
            return s.query(Link).filter(Link.code == code).one().clicks

    return _get


def future(days=1):
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def past(days=1):
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
