from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Idea, IdeaWant

URL = "/api/v1/couple/ideas"
Headers = dict[str, str]
MakeCouple = Callable[[], tuple[Headers, Headers]]


def add(client: TestClient, headers: Headers, **fields: object) -> dict:
    payload = {"title": "Каток", "format": "active", **fields}
    response = client.post(URL, headers=headers, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_and_both_see_it(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    idea = add(
        client,
        mila,
        title="Хинкали",
        format="food",
        cuisine="georgian",
        budget="medium",
        times_of_day=["evening", "day", "evening"],
    )
    assert idea["times_of_day"] == ["day", "evening"]  # deduplicated, in day order
    assert idea["wanted_by"] == [idea["author_id"]]  # author's ❤️ is there from the start
    assert idea["both_want"] is False
    assert idea["is_done"] is False

    ideas = client.get(URL, headers=sasha).json()
    assert [i["title"] for i in ideas] == ["Хинкали"]


def test_other_couples_cannot_see_or_touch(
    client: TestClient, make_couple: MakeCouple, make_user: Callable[[str], Headers]
) -> None:
    mila, _ = make_couple()
    idea = add(client, mila)

    stranger = make_user("Stranger")
    client.post("/api/v1/couple", headers=stranger, json={})
    assert client.get(URL, headers=stranger).json() == []
    for method in ("get", "patch", "delete"):
        kwargs = {"json": {"title": "x"}} if method == "patch" else {}
        response = getattr(client, method)(f"{URL}/{idea['id']}", headers=stranger, **kwargs)
        assert response.status_code == 404

    assert client.get(URL, headers=make_user("Single")).status_code == 404  # no couple yet


def test_cuisine_only_for_food(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    response = client.post(
        URL, headers=mila, json={"title": "Каток", "format": "active", "cuisine": "italian"}
    )
    assert response.status_code == 422

    idea = add(client, mila, title="Паста", format="food", cuisine="italian")
    # Moving out of food quietly drops the cuisine...
    moved = client.patch(f"{URL}/{idea['id']}", headers=mila, json={"format": "home"}).json()
    assert moved["format"] == "home" and moved["cuisine"] is None
    # ...but explicitly setting a cuisine on a non-food idea is an error.
    response = client.patch(f"{URL}/{idea['id']}", headers=mila, json={"cuisine": "italian"})
    assert response.status_code == 422


def test_update_changes_only_sent_fields(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    idea = add(client, mila, budget="low", link="https://example.com")
    updated = client.patch(f"{URL}/{idea['id']}", headers=mila, json={"title": "Каток в парке"})
    assert updated.json()["title"] == "Каток в парке"
    assert updated.json()["budget"] == "low"
    assert updated.json()["link"] == "https://example.com"

    assert (
        client.patch(f"{URL}/{idea['id']}", headers=mila, json={"title": None}).status_code == 422
    )
    assert client.patch(f"{URL}/{idea['id']}", headers=mila, json={"x": 1}).status_code == 422


def test_want_both(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    idea = add(client, mila)

    liked = client.post(f"{URL}/{idea['id']}/want", headers=sasha).json()
    assert len(liked["wanted_by"]) == 2 and liked["both_want"] is True
    # Pressing twice changes nothing.
    assert (
        client.post(f"{URL}/{idea['id']}/want", headers=sasha).json()["wanted_by"]
        == liked["wanted_by"]
    )

    unliked = client.delete(f"{URL}/{idea['id']}/want", headers=sasha).json()
    assert unliked["both_want"] is False and len(unliked["wanted_by"]) == 1


def test_done_and_undone(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    idea = add(client, mila)

    done = client.post(
        f"{URL}/{idea['id']}/done",
        headers=mila,
        json={"rating": 5, "review": "Холодно, но классно"},
    )
    assert done.status_code == 200
    assert done.json()["is_done"] is True
    assert done.json()["done_at"] is not None
    assert done.json()["rating"] == 5

    assert (
        client.post(f"{URL}/{idea['id']}/done", headers=mila, json={"rating": 6}).status_code == 422
    )

    undone = client.post(f"{URL}/{idea['id']}/undone", headers=mila).json()
    assert undone["is_done"] is False
    assert undone["done_at"] is None and undone["rating"] is None and undone["review"] is None


def test_list_filters_and_order(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    cinema = add(client, mila, title="Кино", format="culture", budget="low")
    sushi = add(client, mila, title="Суши", format="food", budget="high")
    walk = add(client, mila, title="Прогулка", format="walk")  # no budget = not decided
    client.post(f"{URL}/{cinema['id']}/done", headers=mila, json={})
    client.post(f"{URL}/{sushi['id']}/want", headers=sasha)

    def titles(**params: object) -> list[str]:
        return [i["title"] for i in client.get(URL, headers=mila, params=params).json()]

    assert titles() == ["Прогулка", "Суши", "Кино"]  # not done first, newest first
    assert titles(format="food") == ["Суши"]
    assert titles(is_done=True) == ["Кино"]
    assert titles(max_budget="medium") == ["Прогулка", "Кино"]
    assert titles(both_want=True) == ["Суши"]
    assert titles(both_want=False) == ["Прогулка", "Кино"]
    assert walk["budget"] is None


def test_delete(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    idea = add(client, mila)
    client.post(f"{URL}/{idea['id']}/want", headers=sasha)
    assert client.delete(f"{URL}/{idea['id']}", headers=sasha).status_code == 204
    assert client.get(f"{URL}/{idea['id']}", headers=mila).status_code == 404


def test_ideas_deleted_with_couple(
    client: TestClient, db_session: Session, make_user: Callable[[str], Headers]
) -> None:
    mila = make_user("Mila")
    client.post("/api/v1/couple", headers=mila, json={})
    idea = add(client, mila)
    client.post("/api/v1/couple/leave", headers=mila)  # last member leaves -> couple deleted

    db_session.expire_all()
    assert db_session.get(Idea, idea["id"]) is None
    assert db_session.scalar(select(func.count()).select_from(IdeaWant)) == 0
