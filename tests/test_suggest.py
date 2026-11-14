from collections.abc import Callable

from fastapi.testclient import TestClient

from app.catalog import ACTIVITIES, ACTIVITIES_BY_ID

IDEAS = "/api/v1/couple/ideas"
SUGGEST = f"{IDEAS}/suggest"
Headers = dict[str, str]
MakeCouple = Callable[[], tuple[Headers, Headers]]


def test_own_idea_comes_first(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    idea = client.post(
        IDEAS,
        headers=mila,
        json={"title": "Наш каток", "format": "active", "times_of_day": ["evening"]},
    ).json()

    for _ in range(10):  # random, but there is only one matching idea
        result = client.get(SUGGEST, headers=sasha, params={"format": "active"}).json()
        assert result["source"] == "idea"
        assert result["idea"]["id"] == idea["id"]
        assert result["activity"] is None


def test_falls_back_to_catalog(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    client.post(
        IDEAS,
        headers=mila,
        json={"title": "Наш каток", "format": "active", "times_of_day": ["evening"]},
    )

    # The own idea is for the evening, so in the morning the catalog helps out.
    result = client.get(
        SUGGEST, headers=mila, params={"format": "active", "time_of_day": "morning"}
    ).json()
    assert result["source"] == "catalog"
    activity = ACTIVITIES_BY_ID[result["activity"]["id"]]
    assert activity.format == "active" and "morning" in activity.times_of_day


def test_done_ideas_are_not_suggested(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    idea = client.post(IDEAS, headers=mila, json={"title": "Каток", "format": "active"}).json()
    client.post(f"{IDEAS}/{idea['id']}/done", headers=mila, json={})
    assert (
        client.get(SUGGEST, headers=mila, params={"format": "active"}).json()["source"] == "catalog"
    )


def test_all_filters_respected(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    params = {"format": "food", "cuisine": "japanese", "time_of_day": "night", "max_budget": "low"}
    for _ in range(10):
        activity = client.get(SUGGEST, headers=mila, params=params).json()["activity"]
        assert activity["id"] == "ramen"  # the only cheap Japanese place open at night


def test_more_button_excludes_shown(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    a = client.post(IDEAS, headers=mila, json={"title": "Рамен", "format": "food"}).json()
    b = client.post(IDEAS, headers=mila, json={"title": "Суши", "format": "food"}).json()

    first = client.get(SUGGEST, headers=mila, params={"format": "food"}).json()["idea"]["id"]
    second = client.get(
        SUGGEST, headers=mila, params={"format": "food", "exclude_ideas": [first]}
    ).json()
    assert second["idea"]["id"] == ({a["id"], b["id"]} - {first}).pop()

    third = client.get(
        SUGGEST, headers=mila, params={"format": "food", "exclude_ideas": [a["id"], b["id"]]}
    )
    assert third.json()["source"] == "catalog"


def test_nothing_matches(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    every_walk = [a.id for a in ACTIVITIES if a.format == "walk"]
    response = client.get(
        SUGGEST, headers=mila, params={"format": "walk", "exclude_catalog": every_walk}
    )
    assert response.status_code == 404


def test_save_from_catalog(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    response = client.post(f"{IDEAS}/from-catalog/ramen", headers=mila)
    assert response.status_code == 201
    idea = response.json()
    assert (
        idea["title"] == "Рамен" and idea["cuisine"] == "japanese" and idea["catalog_id"] == "ramen"
    )

    assert client.post(f"{IDEAS}/from-catalog/ramen", headers=mila).status_code == 409
    assert client.post(f"{IDEAS}/from-catalog/no-such-thing", headers=mila).status_code == 404

    # Saved, so now it comes back as the couple's own idea, not from the catalog.
    params = {"format": "food", "cuisine": "japanese", "time_of_day": "night", "max_budget": "low"}
    result = client.get(SUGGEST, headers=mila, params=params).json()
    assert result["source"] == "idea" and result["idea"]["id"] == idea["id"]


def test_catalog_is_public_and_filterable(client: TestClient) -> None:
    everything = client.get("/api/v1/catalog/activities").json()
    assert len(everything) == len(ACTIVITIES)
    georgian = client.get("/api/v1/catalog/activities", params={"cuisine": "georgian"}).json()
    assert [a["id"] for a in georgian] == ["georgian"]


def test_catalog_is_consistent() -> None:
    for a in ACTIVITIES:
        assert a.times_of_day, a.id
        assert a.cuisine is None or a.format == "food", a.id
