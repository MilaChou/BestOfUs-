from collections.abc import Callable
from datetime import date, timedelta

from fastapi.testclient import TestClient

URL = "/api/v1/couple/tasks"
Headers = dict[str, str]
MakeCouple = Callable[[], tuple[Headers, Headers]]


def me(client: TestClient, headers: Headers) -> int:
    return client.get("/api/v1/users/me", headers=headers).json()["id"]


def add(client: TestClient, headers: Headers, **fields: object) -> dict:
    response = client.post(URL, headers=headers, json={"title": "Купить продукты", **fields})
    assert response.status_code == 201, response.text
    return response.json()


def test_create_and_both_see(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    task = add(client, mila, category="shopping", note="молоко, хлеб")
    assert task["assignee_id"] is None and task["is_done"] is False and task["is_overdue"] is False
    assert [t["title"] for t in client.get(URL, headers=sasha).json()] == ["Купить продукты"]


def test_assignee_must_be_in_couple(
    client: TestClient, make_couple: MakeCouple, make_user: Callable[[str], Headers]
) -> None:
    mila, sasha = make_couple()
    stranger_id = me(client, make_user("Stranger"))
    assert (
        client.post(URL, headers=mila, json={"title": "x", "assignee_id": stranger_id}).status_code
        == 422
    )

    task = add(client, mila, assignee_id=me(client, sasha))
    assert task["assignee_id"] == me(client, sasha)
    response = client.patch(f"{URL}/{task['id']}", headers=mila, json={"assignee_id": stranger_id})
    assert response.status_code == 422
    # Back to "both of us".
    assert (
        client.patch(f"{URL}/{task['id']}", headers=mila, json={"assignee_id": None}).json()[
            "assignee_id"
        ]
        is None
    )


def test_done_records_who(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    task = add(client, mila)
    done = client.post(f"{URL}/{task['id']}/done", headers=sasha).json()
    assert done["is_done"] is True and done["done_by_id"] == me(client, sasha) and done["done_at"]
    undone = client.post(f"{URL}/{task['id']}/undone", headers=mila).json()
    assert undone["is_done"] is False and undone["done_by_id"] is None and undone["done_at"] is None


def test_filters_and_order(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    today = date.today()
    add(client, mila, title="Без даты")
    add(client, mila, title="Через месяц", due_date=str(today + timedelta(days=30)))
    add(client, mila, title="Сегодня", due_date=str(today), category="health")
    late = add(client, mila, title="Просрочено", due_date=str(today - timedelta(days=2)))
    add(
        client,
        mila,
        title="Саше",
        due_date=str(today + timedelta(days=3)),
        assignee_id=me(client, sasha),
    )
    done = add(client, mila, title="Сделано")
    client.post(f"{URL}/{done['id']}/done", headers=mila)

    def titles(headers: Headers = mila, **params: object) -> list[str]:
        return [t["title"] for t in client.get(URL, headers=headers, params=params).json()]

    assert titles() == ["Просрочено", "Сегодня", "Саше", "Через месяц", "Без даты", "Сделано"]
    assert late["is_overdue"] is True
    assert titles(due="overdue") == ["Просрочено"]
    assert titles(due="today") == ["Сегодня"]
    assert titles(due="week") == ["Сегодня", "Саше"]
    assert titles(category="health") == ["Сегодня"]
    assert titles(is_done=True) == ["Сделано"]
    assert "Саше" not in titles(for_me=True)  # assigned to Sasha only
    assert "Саше" in titles(sasha, for_me=True)
    assert "Без даты" in titles(sasha, for_me=True)  # "both of us" counts for everyone


def test_update_delete_and_privacy(
    client: TestClient, make_couple: MakeCouple, make_user: Callable[[str], Headers]
) -> None:
    mila, _ = make_couple()
    task = add(client, mila)
    updated = client.patch(
        f"{URL}/{task['id']}", headers=mila, json={"title": "Купить продукты на неделю"}
    ).json()
    assert updated["title"] == "Купить продукты на неделю"
    assert (
        client.patch(f"{URL}/{task['id']}", headers=mila, json={"title": None}).status_code == 422
    )

    stranger = make_user("Stranger")
    client.post("/api/v1/couple", headers=stranger, json={})
    assert client.get(f"{URL}/{task['id']}", headers=stranger).status_code == 404
    assert client.delete(f"{URL}/{task['id']}", headers=stranger).status_code == 404

    assert client.delete(f"{URL}/{task['id']}", headers=mila).status_code == 204
    assert client.get(URL, headers=mila).json() == []
