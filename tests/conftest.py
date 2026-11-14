import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")

from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture
def db_session() -> Iterator[Session]:
    """Fresh in-memory database for every test, so tests never touch bestofus.db."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as session:
        yield session
    engine.dispose()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(client: TestClient) -> Callable[[str], dict[str, str]]:
    """Register a user and return auth headers for them: headers = make_user("Mila")."""

    def _make_user(name: str) -> dict[str, str]:
        email = f"{name.lower()}@example.com"
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": "secret123", "name": name},
        )
        response = client.post(
            "/api/v1/auth/login", data={"username": email, "password": "secret123"}
        )
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return _make_user
