from collections.abc import Callable

from fastapi.testclient import TestClient

from app.gift_catalog import GIFTS

NOTES = "/api/v1/gift-notes"
SUGGEST = "/api/v1/gifts/suggest"
Headers = dict[str, str]
MakeCouple = Callable[[], tuple[Headers, Headers]]


# --- Secret notes ----------------------------------------------------------


def test_notes_are_private(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    note = client.post(NOTES, headers=mila, json={"title": "Кружка с котом", "price": 800}).json()
    assert note["budget"] == "low"

    assert [n["title"] for n in client.get(NOTES, headers=mila).json()] == ["Кружка с котом"]
    assert client.get(NOTES, headers=sasha).json() == []
    assert (
        client.patch(f"{NOTES}/{note['id']}", headers=sasha, json={"title": "x"}).status_code == 404
    )
    assert client.delete(f"{NOTES}/{note['id']}", headers=sasha).status_code == 404


def test_note_update_gifted_and_delete(
    client: TestClient, make_user: Callable[[str], Headers]
) -> None:
    mila = make_user("Mila")
    note = client.post(NOTES, headers=mila, json={"title": "Шарф"}).json()
    gifted = client.patch(f"{NOTES}/{note['id']}", headers=mila, json={"is_gifted": True}).json()
    assert gifted["is_gifted"] is True and gifted["title"] == "Шарф"
    assert client.get(NOTES, headers=mila, params={"is_gifted": False}).json() == []
    assert client.delete(f"{NOTES}/{note['id']}", headers=mila).status_code == 204


# --- «Что подарить?» -------------------------------------------------------


def test_partner_wish_comes_first(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    wish = client.post(
        "/api/v1/wishlist/me", headers=sasha, json={"title": "Наушники", "gift_type": "tech"}
    ).json()
    client.post(NOTES, headers=mila, json={"title": "Колонка", "gift_type": "tech"})

    result = client.get(SUGGEST, headers=mila, params={"gift_type": "tech"}).json()
    assert result["source"] == "wishlist" and result["wish"]["id"] == wish["id"]


def test_reserved_and_received_wishes_skipped(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    a = client.post(
        "/api/v1/wishlist/me", headers=sasha, json={"title": "A", "gift_type": "tech"}
    ).json()
    b = client.post(
        "/api/v1/wishlist/me", headers=sasha, json={"title": "B", "gift_type": "tech"}
    ).json()
    client.post(f"/api/v1/wishlist/partner/{a['id']}/reserve", headers=mila)
    client.post(f"/api/v1/wishlist/me/{b['id']}/received", headers=sasha)
    assert (
        client.get(SUGGEST, headers=mila, params={"gift_type": "tech"}).json()["source"]
        != "wishlist"
    )


def test_notes_then_catalog(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    note = client.post(
        NOTES, headers=mila, json={"title": "Кружка", "gift_type": "home", "price": 500}
    ).json()

    result = client.get(SUGGEST, headers=mila, params={"gift_type": "home", "budget": "low"}).json()
    assert result["source"] == "note" and result["note"]["id"] == note["id"]

    result = client.get(
        SUGGEST,
        headers=mila,
        params={"gift_type": "home", "budget": "low", "exclude_notes": [note["id"]]},
    ).json()
    assert result["source"] == "catalog"
    assert result["gift"]["gift_type"] == "home" and result["gift"]["budget"] == "low"


def test_filters_respected(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    for _ in range(15):
        gift = client.get(
            SUGGEST, headers=mila, params={"gift_type": "together", "budget": "free"}
        ).json()["gift"]
        assert gift["id"] in {"coupon-book", "treasure-hunt"}


def test_personalized_from_profile(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    client.patch(
        "/api/v1/users/me/profile",
        headers=sasha,
        json={"favorite_flowers": "пионы", "allergies": "лилии"},
    )

    gift = client.get(
        SUGGEST, headers=mila, params={"gift_type": "small_joy", "budget": "low"}
    ).json()
    assert (
        gift["gift"]["id"] == "personal-flowers"
    )  # personal gifts come before the general catalog
    assert gift["gift"]["title"] == "Букет: пионы"
    assert gift["gift"]["personalized"] is True
    assert "пионы" in gift["gift"]["hint"]
    assert gift["warning"] == "Проверь аллергии партнёра: лилии"

    # Not allergy-sensitive -> no warning.
    other = client.get(SUGGEST, headers=mila, params={"gift_type": "tech"}).json()
    assert other["warning"] is None


def test_save_catalog_gift_to_notes(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    client.patch("/api/v1/users/me/profile", headers=sasha, json={"ring_size": "17"})

    saved = client.post(f"{NOTES}/from-catalog/personal-ring", headers=mila)
    assert saved.status_code == 201 and saved.json()["title"] == "Кольцо — размер 17"
    assert client.post(f"{NOTES}/from-catalog/personal-ring", headers=mila).status_code == 409
    assert client.post(f"{NOTES}/from-catalog/puzzle", headers=mila).status_code == 201
    assert client.post(f"{NOTES}/from-catalog/nope", headers=mila).status_code == 404

    # Saved items now come back as notes, not as catalog gifts.
    result = client.get(
        SUGGEST, headers=mila, params={"gift_type": "clothes", "budget": "high"}
    ).json()
    assert result["source"] == "note"


def test_works_without_partner(client: TestClient, make_user: Callable[[str], Headers]) -> None:
    mila = make_user("Mila")
    result = client.get(SUGGEST, headers=mila).json()
    assert result["source"] == "catalog" and result["gift"]["personalized"] is False


def test_nothing_matches(client: TestClient, make_couple: MakeCouple) -> None:
    mila, _ = make_couple()
    all_tech = [g.id for g in GIFTS if g.gift_type == "tech"]
    response = client.get(
        SUGGEST, headers=mila, params={"gift_type": "tech", "exclude_catalog": all_tech}
    )
    assert response.status_code == 404


def test_public_catalog(client: TestClient) -> None:
    assert len(client.get("/api/v1/gifts/catalog").json()) == len(GIFTS)
    free = client.get("/api/v1/gifts/catalog", params={"budget": "free"}).json()
    assert {g["id"] for g in free} == {
        "letter",
        "coupon-book",
        "playlist",
        "video-card",
        "treasure-hunt",
    }
