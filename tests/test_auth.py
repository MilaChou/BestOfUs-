from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.security import verify_password

URL = "/api/v1/auth/register"


def test_register_creates_user_and_profile(client: TestClient, db_session: Session) -> None:
    response = client.post(
        URL, json={"email": "Mila@Example.com", "password": "secret123", "name": "Mila"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "mila@example.com"
    assert body["profile"]["name"] == "Mila"
    assert body["profile"]["ring_size"] is None
    assert "password" not in body and "hashed_password" not in body

    user = db_session.scalar(select(User).where(User.email == "mila@example.com"))
    assert user is not None
    assert user.hashed_password != "secret123"
    assert verify_password("secret123", user.hashed_password)


def test_register_duplicate_email(client: TestClient) -> None:
    payload = {"email": "a@example.com", "password": "secret123", "name": "A"}
    assert client.post(URL, json=payload).status_code == 201

    payload["email"] = "A@EXAMPLE.COM"
    response = client.post(URL, json=payload)
    assert response.status_code == 409


def test_register_validation(client: TestClient) -> None:
    bad = [
        {"email": "not-an-email", "password": "secret123", "name": "A"},
        {"email": "b@example.com", "password": "short", "name": "A"},
        {"email": "b@example.com", "password": "secret123", "name": ""},
    ]
    for payload in bad:
        assert client.post(URL, json=payload).status_code == 422
