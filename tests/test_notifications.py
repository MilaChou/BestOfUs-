from collections.abc import Callable

from fastapi.testclient import TestClient

Headers = dict[str, str]
MakeCouple = Callable[[], tuple[Headers, Headers]]
API = "/api/v1"


def bell(client: TestClient, headers: Headers) -> list[dict]:
    return client.get(f"{API}/notifications", headers=headers).json()


def register_phone(client: TestClient, headers: Headers, token: str) -> None:
    response = client.post(
        f"{API}/devices", headers=headers, json={"push_token": token, "platform": "ios"}
    )
    assert response.status_code == 204


def my_id(client: TestClient, headers: Headers) -> int:
    return client.get(f"{API}/users/me", headers=headers).json()["id"]


def test_partner_joined(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    [joined] = bell(client, mila)
    assert joined["type"] == "partner_joined" and joined["body"].startswith("Sasha:")
    assert bell(client, sasha) == []


def test_task_added_goes_to_partner_only(
    client: TestClient, make_couple: MakeCouple, pushed: list
) -> None:
    mila, sasha = make_couple()
    register_phone(client, sasha, "ExponentPushToken[sasha]")
    register_phone(client, mila, "ExponentPushToken[mila]")

    task = client.post(
        f"{API}/couple/tasks",
        headers=mila,
        json={"title": "Купить продукты", "due_date": "2030-11-20"},
    ).json()

    newest = bell(client, sasha)[0]
    assert newest["type"] == "task_added"
    assert newest["title"] == "Новая задача"
    assert newest["body"] == "Mila: «Купить продукты», до 20.11"
    assert newest["data"] == {"task_id": task["id"]}
    assert newest["actor_id"] == my_id(client, mila)

    assert [p["to"] for p in pushed] == ["ExponentPushToken[sasha]"]  # pushed to Sasha's phone only
    assert pushed[0]["data"]["task_id"] == task["id"]
    assert all(n["type"] != "task_added" for n in bell(client, mila))  # no note to yourself


def test_task_assigned_and_done(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    sasha_id = my_id(client, sasha)
    task = client.post(
        f"{API}/couple/tasks", headers=mila, json={"title": "Врач", "assignee_id": sasha_id}
    ).json()
    assert bell(client, sasha)[0]["title"] == "Задача для тебя"

    client.post(f"{API}/couple/tasks/{task['id']}/done", headers=sasha)
    assert bell(client, mila)[0]["type"] == "task_done"
    client.post(f"{API}/couple/tasks/{task['id']}/done", headers=sasha)  # twice -> one notification
    assert sum(n["type"] == "task_done" for n in bell(client, mila)) == 1


def test_reassign_notifies_but_plain_edit_does_not(
    client: TestClient, make_couple: MakeCouple
) -> None:
    mila, sasha = make_couple()
    task = client.post(f"{API}/couple/tasks", headers=mila, json={"title": "Врач"}).json()
    before = len(bell(client, sasha))
    client.patch(f"{API}/couple/tasks/{task['id']}", headers=mila, json={"note": "в 10:00"})
    assert len(bell(client, sasha)) == before
    client.patch(
        f"{API}/couple/tasks/{task['id']}", headers=mila, json={"assignee_id": my_id(client, sasha)}
    )
    assert bell(client, sasha)[0]["type"] == "task_assigned"


def test_ideas_memories_photos_wishes_love_language(
    client: TestClient, make_couple: MakeCouple
) -> None:
    mila, sasha = make_couple()
    idea = client.post(
        f"{API}/couple/ideas", headers=mila, json={"title": "Каток", "format": "active"}
    ).json()
    assert bell(client, sasha)[0]["type"] == "idea_added"

    client.post(f"{API}/couple/ideas/{idea['id']}/want", headers=sasha)
    assert bell(client, mila)[0]["title"] == "Вы оба этого хотите!"

    memory = client.post(f"{API}/couple/memories", headers=sasha, json={"title": "Каток"}).json()
    assert bell(client, mila)[0]["type"] == "memory_added"
    jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 50
    client.post(
        f"{API}/couple/memories/{memory['id']}/photos",
        headers=sasha,
        files=[("files", ("a.jpg", jpeg, "image/jpeg"))] * 2,
    )
    assert bell(client, mila)[0]["body"] == "Sasha: 2 фото в «Каток»"

    client.post(f"{API}/wishlist/me", headers=mila, json={"title": "Пазл"})
    assert bell(client, sasha)[0]["type"] == "wish_added"

    answers = {str(i): "a" for i in range(1, 31)}
    client.post(f"{API}/tests/love", headers=sasha, json={"answers": answers})
    assert bell(client, mila)[0]["type"] == "love_language_done"


def test_secrets_never_notify(client: TestClient, make_couple: MakeCouple, pushed: list) -> None:
    mila, sasha = make_couple()
    wish = client.post(f"{API}/wishlist/me", headers=mila, json={"title": "Пазл"}).json()
    mila_before, pushed_before = bell(client, mila), len(pushed)

    client.post(f"{API}/wishlist/partner/{wish['id']}/reserve", headers=sasha)
    client.delete(f"{API}/wishlist/partner/{wish['id']}/reserve", headers=sasha)
    client.post(f"{API}/gift-notes", headers=sasha, json={"title": "Кружка"})
    client.post(f"{API}/gift-notes/from-catalog/puzzle", headers=sasha)

    assert bell(client, mila) == mila_before
    assert len(pushed) == pushed_before


def test_muted_category_no_push_but_in_list(
    client: TestClient, make_couple: MakeCouple, pushed: list
) -> None:
    mila, sasha = make_couple()
    register_phone(client, sasha, "ExponentPushToken[sasha]")

    settings = client.get(f"{API}/notifications/settings", headers=sasha).json()
    assert all(settings.values()) and "tasks" in settings and "birthday" in settings

    updated = client.patch(
        f"{API}/notifications/settings", headers=sasha, json={"tasks": False}
    ).json()
    assert updated["tasks"] is False and updated["ideas"] is True

    client.post(f"{API}/couple/tasks", headers=mila, json={"title": "Тихая задача"})
    assert bell(client, sasha)[0]["type"] == "task_added"
    assert pushed == []

    client.post(f"{API}/couple/ideas", headers=mila, json={"title": "Каток", "format": "active"})
    assert len(pushed) == 1

    back = client.patch(f"{API}/notifications/settings", headers=sasha, json={"tasks": True}).json()
    assert back["tasks"] is True
    assert (
        client.patch(
            f"{API}/notifications/settings", headers=sasha, json={"nope": False}
        ).status_code
        == 422
    )


def test_read_and_unread_count(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    for title in ("A", "B", "C"):
        client.post(f"{API}/couple/tasks", headers=mila, json={"title": title})
    count = lambda: client.get(f"{API}/notifications/unread-count", headers=sasha).json()["unread"]  # noqa: E731
    assert count() == 3

    first = bell(client, sasha)[0]
    read = client.post(f"{API}/notifications/{first['id']}/read", headers=sasha).json()
    assert read["is_read"] is True and read["read_at"]
    assert count() == 2
    assert (
        len(client.get(f"{API}/notifications", headers=sasha, params={"unread_only": True}).json())
        == 2
    )

    assert (
        client.post(f"{API}/notifications/{first['id']}/read", headers=mila).status_code == 404
    )  # not hers
    assert client.post(f"{API}/notifications/read-all", headers=sasha).status_code == 204
    assert count() == 0


def test_paging(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    for i in range(5):
        client.post(f"{API}/couple/tasks", headers=mila, json={"title": f"T{i}"})
    page = client.get(
        f"{API}/notifications", headers=sasha, params={"limit": 2, "offset": 1}
    ).json()
    assert [n["body"] for n in page] == ["Mila: «T3»", "Mila: «T2»"]


def test_devices(client: TestClient, make_couple: MakeCouple, pushed: list) -> None:
    mila, sasha = make_couple()
    register_phone(client, sasha, "ExponentPushToken[phone]")
    register_phone(client, sasha, "ExponentPushToken[phone]")  # twice is fine
    # The same phone logs into Mila's account -> it now belongs to Mila.
    register_phone(client, mila, "ExponentPushToken[phone]")
    client.post(f"{API}/couple/tasks", headers=mila, json={"title": "x"})
    assert pushed == []  # Sasha has no phone any more

    client.post(
        f"{API}/devices",
        headers=sasha,
        json={"push_token": "ExponentPushToken[new]", "platform": "android"},
    )
    client.request(
        "DELETE", f"{API}/devices", headers=sasha, json={"push_token": "ExponentPushToken[new]"}
    )
    client.post(f"{API}/couple/tasks", headers=mila, json={"title": "y"})
    assert pushed == []


def test_texts_have_no_emoji(client: TestClient, make_couple: MakeCouple) -> None:
    """The app is designed without emoji, so notification texts must not have them either."""
    import re

    mila, sasha = make_couple()
    client.post(f"{API}/couple/tasks", headers=mila, json={"title": "x"})
    client.post(f"{API}/couple/ideas", headers=mila, json={"title": "y", "format": "home"})
    emoji = re.compile("[\U0001f300-\U0001faff☀-➿]")
    for n in bell(client, sasha) + bell(client, mila):
        assert not emoji.search(n["title"] + n["body"]), n
