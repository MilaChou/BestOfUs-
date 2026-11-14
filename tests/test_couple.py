from collections.abc import Callable
from datetime import date, timedelta

from fastapi.testclient import TestClient

URL = "/api/v1/couple"
MakeUser = Callable[[str], dict[str, str]]


def test_create_and_join(client: TestClient, make_user: MakeUser) -> None:
    mila, sasha = make_user("Mila"), make_user("Sasha")

    response = client.post(URL, headers=mila, json={"name": "Mila & Sasha"})
    assert response.status_code == 201
    couple = response.json()
    code = couple["invite_code"]
    assert len(code) == 8
    assert [m["profile"]["name"] for m in couple["members"]] == ["Mila"]

    # Code works regardless of case and stray spaces.
    response = client.post(f"{URL}/join", headers=sasha, json={"invite_code": f" {code.lower()} "})
    assert response.status_code == 200
    couple = response.json()
    assert [m["profile"]["name"] for m in couple["members"]] == ["Mila", "Sasha"]
    assert couple["invite_code"] is None  # full, code no longer needed

    # Both see the same couple, including the partner's profile.
    for headers in (mila, sasha):
        assert client.get(URL, headers=headers).json()["id"] == couple["id"]


def test_partner_sees_profile(client: TestClient, make_user: MakeUser) -> None:
    mila, sasha = make_user("Mila"), make_user("Sasha")
    client.patch("/api/v1/users/me/profile", headers=mila, json={"ring_size": "16.5"})
    code = client.post(URL, headers=mila, json={}).json()["invite_code"]
    client.post(f"{URL}/join", headers=sasha, json={"invite_code": code})

    members = client.get(URL, headers=sasha).json()["members"]
    assert members[0]["profile"]["ring_size"] == "16.5"


def test_cannot_be_in_two_couples(client: TestClient, make_user: MakeUser) -> None:
    mila, sasha = make_user("Mila"), make_user("Sasha")
    code = client.post(URL, headers=mila, json={}).json()["invite_code"]

    assert client.post(URL, headers=mila, json={}).status_code == 409
    assert client.post(f"{URL}/join", headers=mila, json={"invite_code": code}).status_code == 409

    client.post(URL, headers=sasha, json={})
    assert client.post(f"{URL}/join", headers=sasha, json={"invite_code": code}).status_code == 409


def test_third_person_cannot_join(client: TestClient, make_user: MakeUser) -> None:
    mila, sasha, extra = make_user("Mila"), make_user("Sasha"), make_user("Extra")
    code = client.post(URL, headers=mila, json={}).json()["invite_code"]
    client.post(f"{URL}/join", headers=sasha, json={"invite_code": code})

    response = client.post(f"{URL}/join", headers=extra, json={"invite_code": code})
    assert response.status_code == 404  # code was cleared when the couple filled up


def test_invalid_code(client: TestClient, make_user: MakeUser) -> None:
    response = client.post(
        f"{URL}/join", headers=make_user("Mila"), json={"invite_code": "NOPE1234"}
    )
    assert response.status_code == 404


def test_no_couple_yet(client: TestClient, make_user: MakeUser) -> None:
    mila = make_user("Mila")
    assert client.get(URL, headers=mila).status_code == 404
    assert client.patch(URL, headers=mila, json={"name": "x"}).status_code == 404
    assert client.post(f"{URL}/leave", headers=mila).status_code == 404
    assert client.get(URL).status_code == 401


def test_update_and_days_together(client: TestClient, make_user: MakeUser) -> None:
    mila = make_user("Mila")
    client.post(URL, headers=mila, json={})
    since = date.today() - timedelta(days=365)

    response = client.patch(URL, headers=mila, json={"together_since": since.isoformat()})
    assert response.status_code == 200
    assert response.json()["days_together"] == 365
    assert response.json()["name"] is None

    response = client.patch(URL, headers=mila, json={"name": "Us"})
    assert response.json()["name"] == "Us"
    assert response.json()["together_since"] == since.isoformat()


def test_leave(client: TestClient, make_user: MakeUser) -> None:
    mila, sasha, new = make_user("Mila"), make_user("Sasha"), make_user("New")
    code = client.post(URL, headers=mila, json={}).json()["invite_code"]
    client.post(f"{URL}/join", headers=sasha, json={"invite_code": code})

    assert client.post(f"{URL}/leave", headers=sasha).status_code == 204
    assert client.get(URL, headers=sasha).status_code == 404

    # The one who stays gets a fresh code and can invite again.
    couple = client.get(URL, headers=mila).json()
    assert len(couple["members"]) == 1
    new_code = couple["invite_code"]
    assert new_code and new_code != code
    assert (
        client.post(f"{URL}/join", headers=new, json={"invite_code": new_code}).status_code == 200
    )

    # Sasha is free to start a new couple.
    assert client.post(URL, headers=sasha, json={}).status_code == 201


def test_last_member_leaving_deletes_couple(client: TestClient, make_user: MakeUser) -> None:
    mila = make_user("Mila")
    code = client.post(URL, headers=mila, json={}).json()["invite_code"]
    assert client.post(f"{URL}/leave", headers=mila).status_code == 204

    response = client.post(f"{URL}/join", headers=make_user("Sasha"), json={"invite_code": code})
    assert response.status_code == 404
