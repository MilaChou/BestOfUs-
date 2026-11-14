from collections.abc import Callable
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient

URL = "/api/v1/couple/memories"
Headers = dict[str, str]
MakeCouple = Callable[[], tuple[Headers, Headers]]

# Smallest real file headers — enough for the type check.
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


def add(client: TestClient, headers: Headers, **fields: object) -> dict:
    response = client.post(URL, headers=headers, json={"title": "Первое свидание", **fields})
    assert response.status_code == 201, response.text
    return response.json()


def upload(client: TestClient, headers: Headers, memory_id: int, *files: tuple[str, bytes]):
    return client.post(
        f"{URL}/{memory_id}/photos",
        headers=headers,
        files=[("files", (name, data, "image/jpeg")) for name, data in files],
    )


def stored_files(media_dir: Path) -> list[Path]:
    folder = media_dir / "memories"
    return sorted(folder.iterdir()) if folder.exists() else []


def test_create_defaults_to_today(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    memory = add(client, mila, place="Парк Горького", description="Было холодно")
    assert memory["happened_on"] == date.today().isoformat()
    assert memory["photos"] == [] and memory["years_ago"] == 0
    assert [m["title"] for m in client.get(URL, headers=sasha).json()] == ["Первое свидание"]


def test_upload_view_delete_photos(
    client: TestClient, make_couple: MakeCouple, media_dir: Path
) -> None:
    mila, sasha = make_couple()
    memory = add(client, mila)

    response = upload(client, mila, memory["id"], ("a.jpg", JPEG), ("b.png", PNG))
    assert response.status_code == 200, response.text
    photos = response.json()["photos"]
    assert [p["content_type"] for p in photos] == ["image/jpeg", "image/png"]
    assert len(stored_files(media_dir)) == 2
    assert all(f.name not in {"a.jpg", "b.png"} for f in stored_files(media_dir))  # random names

    # The partner can open the photo; the bytes are the same.
    picture = client.get(photos[0]["url"], headers=sasha)
    assert picture.status_code == 200
    assert picture.content == JPEG and picture.headers["content-type"] == "image/jpeg"
    assert client.get(photos[0]["url"]).status_code == 401  # no login, no photo

    assert client.delete(photos[0]["url"], headers=mila).status_code == 204
    assert len(stored_files(media_dir)) == 1
    assert len(client.get(f"{URL}/{memory['id']}", headers=mila).json()["photos"]) == 1


def test_rejects_non_images_and_keeps_nothing(
    client: TestClient, make_couple: MakeCouple, media_dir: Path
) -> None:
    mila, _ = make_couple()
    memory = add(client, mila)
    # A text file renamed to .jpg is still not a photo.
    response = upload(
        client, mila, memory["id"], ("ok.jpg", JPEG), ("fake.jpg", b"hello, i am text")
    )
    assert response.status_code == 415
    assert stored_files(media_dir) == []  # the good one was rolled back too
    assert client.get(f"{URL}/{memory['id']}", headers=mila).json()["photos"] == []


def test_size_and_count_limits(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    memory = add(client, mila)
    big = JPEG + b"\x00" * (10 * 1024 * 1024)
    assert upload(client, mila, memory["id"], ("big.jpg", big)).status_code == 413
    assert (
        upload(client, mila, memory["id"], *[(f"{i}.jpg", JPEG) for i in range(11)]).status_code
        == 409
    )
    assert (
        upload(client, mila, memory["id"], *[(f"{i}.jpg", JPEG) for i in range(10)]).status_code
        == 200
    )
    assert upload(client, mila, memory["id"], ("one-more.jpg", JPEG)).status_code == 409


def test_strangers_cannot_see_photos(
    client: TestClient, make_couple: MakeCouple, make_user: Callable[[str], Headers]
) -> None:
    mila, _ = make_couple()
    memory = add(client, mila)
    photo_url = upload(client, mila, memory["id"], ("a.jpg", JPEG)).json()["photos"][0]["url"]
    stranger = make_user("Stranger")
    client.post("/api/v1/couple", headers=stranger, json={})
    assert client.get(photo_url, headers=stranger).status_code == 404
    assert client.get(f"{URL}/{memory['id']}", headers=stranger).status_code == 404


def test_deleting_memory_deletes_files(
    client: TestClient, make_couple: MakeCouple, media_dir: Path
) -> None:
    mila, _ = make_couple()
    memory = add(client, mila)
    upload(client, mila, memory["id"], ("a.jpg", JPEG), ("b.jpg", JPEG))
    assert client.delete(f"{URL}/{memory['id']}", headers=mila).status_code == 204
    assert stored_files(media_dir) == []


def test_last_member_leaving_deletes_files(
    client: TestClient, make_user: Callable[[str], Headers], media_dir: Path
) -> None:
    mila = make_user("Mila")
    client.post("/api/v1/couple", headers=mila, json={})
    memory = add(client, mila)
    upload(client, mila, memory["id"], ("a.jpg", JPEG))
    client.post("/api/v1/couple/leave", headers=mila)
    assert stored_files(media_dir) == []


def test_order_year_and_on_this_day(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    today = date.today()
    try:
        two_years_ago = today.replace(year=today.year - 2)
    except ValueError:  # today is 29 February
        two_years_ago = today.replace(year=today.year - 4)
    add(client, mila, title="Сегодня")
    add(client, mila, title="Годовщина", happened_on=two_years_ago.isoformat())
    add(
        client,
        mila,
        title="Давно",
        happened_on="2015-01-01" if (today.month, today.day) != (1, 1) else "2015-01-02",
    )

    assert [m["title"] for m in client.get(URL, headers=mila).json()] == [
        "Сегодня",
        "Годовщина",
        "Давно",
    ]
    assert [m["title"] for m in client.get(URL, headers=mila, params={"year": 2015}).json()] == [
        "Давно"
    ]
    on_this_day = client.get(f"{URL}/on-this-day", headers=mila).json()
    assert [m["title"] for m in on_this_day] == ["Годовщина"]
    assert on_this_day[0]["years_ago"] == today.year - two_years_ago.year


def test_memory_from_done_idea(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    idea = client.post(
        "/api/v1/couple/ideas", headers=mila, json={"title": "Каток", "format": "active"}
    ).json()

    assert (
        client.post(f"{URL}/from-idea/{idea['id']}", headers=mila).status_code == 409
    )  # not done yet
    client.post(
        f"/api/v1/couple/ideas/{idea['id']}/done",
        headers=mila,
        json={"rating": 5, "review": "Падали и смеялись"},
    )

    response = client.post(f"{URL}/from-idea/{idea['id']}", headers=mila)
    assert response.status_code == 201
    memory = response.json()
    assert memory["title"] == "Каток" and memory["description"] == "Падали и смеялись"
    assert memory["idea_id"] == idea["id"] and memory["happened_on"] == date.today().isoformat()

    assert (
        client.post(f"{URL}/from-idea/{idea['id']}", headers=mila).status_code == 409
    )  # only once
    assert client.post(f"{URL}/from-idea/999", headers=mila).status_code == 404


def test_update(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    memory = add(client, mila, place="Кафе")
    updated = client.patch(
        f"{URL}/{memory['id']}", headers=mila, json={"happened_on": "2024-02-14"}
    ).json()
    assert updated["happened_on"] == "2024-02-14" and updated["place"] == "Кафе"
    assert (
        client.patch(f"{URL}/{memory['id']}", headers=mila, json={"happened_on": None}).status_code
        == 422
    )
