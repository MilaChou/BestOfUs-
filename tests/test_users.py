from fastapi.testclient import TestClient

from app.security import create_access_token

EMAIL, PASSWORD = "mila@example.com", "secret123"


def register_and_login(client: TestClient) -> dict[str, str]:
    client.post(
        "/api/v1/auth/register", json={"email": EMAIL, "password": PASSWORD, "name": "Mila"}
    )
    # OAuth2 login is a form, and the email goes in the "username" field.
    response = client.post(
        "/api/v1/auth/login", data={"username": EMAIL.upper(), "password": PASSWORD}
    )
    assert response.status_code == 200
    token = response.json()
    assert token["token_type"] == "bearer"
    return {"Authorization": f"Bearer {token['access_token']}"}


def test_login_wrong_password(client: TestClient) -> None:
    register_and_login(client)
    response = client.post(
        "/api/v1/auth/login", data={"username": EMAIL, "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_login_unknown_email(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login", data={"username": "nobody@example.com", "password": PASSWORD}
    )
    assert response.status_code == 401


def test_me_requires_token(client: TestClient) -> None:
    assert client.get("/api/v1/users/me").status_code == 401
    bad = {"Authorization": "Bearer not-a-real-token"}
    assert client.get("/api/v1/users/me", headers=bad).status_code == 401
    unknown_user = {"Authorization": f"Bearer {create_access_token(999)}"}
    assert client.get("/api/v1/users/me", headers=unknown_user).status_code == 401


def test_read_me(client: TestClient) -> None:
    headers = register_and_login(client)
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == EMAIL
    assert response.json()["profile"]["name"] == "Mila"


def test_update_profile_changes_only_sent_fields(client: TestClient) -> None:
    headers = register_and_login(client)

    response = client.patch(
        "/api/v1/users/me/profile",
        headers=headers,
        json={"ring_size": "16.5", "favorite_flowers": "peonies", "birth_date": "2000-05-14"},
    )
    assert response.status_code == 200
    profile = response.json()["profile"]
    assert profile["ring_size"] == "16.5"
    assert profile["favorite_flowers"] == "peonies"
    assert profile["birth_date"] == "2000-05-14"
    assert profile["name"] == "Mila"

    # Second update keeps earlier values; null clears a field.
    response = client.patch(
        "/api/v1/users/me/profile",
        headers=headers,
        json={"pet_name": "sunshine", "favorite_flowers": None},
    )
    profile = response.json()["profile"]
    assert profile["pet_name"] == "sunshine"
    assert profile["favorite_flowers"] is None
    assert profile["ring_size"] == "16.5"


def test_update_profile_validation(client: TestClient) -> None:
    headers = register_and_login(client)
    url = "/api/v1/users/me/profile"
    assert client.patch(url, headers=headers, json={"name": ""}).status_code == 422
    assert client.patch(url, headers=headers, json={"name": None}).status_code == 422
    assert client.patch(url, headers=headers, json={"unknown_field": 1}).status_code == 422
    assert client.patch(url, headers=headers, json={"birth_date": "not-a-date"}).status_code == 422
