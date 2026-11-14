from collections.abc import Callable

from fastapi.testclient import TestClient

ME = "/api/v1/wishlist/me"
PARTNER = "/api/v1/wishlist/partner"
Headers = dict[str, str]
MakeCouple = Callable[[], tuple[Headers, Headers]]


def add(client: TestClient, headers: Headers, **fields: object) -> dict:
    response = client.post(ME, headers=headers, json={"title": "Пазл", **fields})
    assert response.status_code == 201, response.text
    return response.json()


def test_add_and_partner_sees(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    wish = add(
        client, mila, price=1500, gift_type="together", priority="burning", note="1000 деталей"
    )
    assert wish["budget"] == "low"
    assert "is_reserved" not in wish and "reserved_by_id" not in wish

    seen = client.get(PARTNER, headers=sasha).json()
    assert [w["title"] for w in seen] == ["Пазл"]
    assert seen[0]["is_reserved"] is False


def test_budget_levels(client: TestClient, make_user: Callable[[str], Headers]) -> None:
    mila = make_user("Mila")
    expected = {None: None, 0: "free", 1999: "low", 2000: "medium", 9999: "medium", 10000: "high"}
    for price, budget in expected.items():
        assert add(client, mila, price=price)["budget"] == budget
    assert client.post(ME, headers=mila, json={"title": "x", "price": -1}).status_code == 422


def test_reservation_is_secret_from_owner(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    wish = add(client, mila)

    reserved = client.post(f"{PARTNER}/{wish['id']}/reserve", headers=sasha)
    assert reserved.status_code == 200 and reserved.json()["is_reserved"] is True

    # The owner sees nothing: no field about reservations at all.
    mine = client.get(ME, headers=mila).json()
    assert mine[0]["id"] == wish["id"]
    assert not any("reserv" in key for key in mine[0])

    # The owner can't reach the partner endpoints for their own wishes either.
    assert client.post(f"{PARTNER}/{wish['id']}/reserve", headers=mila).status_code == 404

    # Cancel.
    cancelled = client.delete(f"{PARTNER}/{wish['id']}/reserve", headers=sasha).json()
    assert cancelled["is_reserved"] is False


def test_owner_view_identical_before_and_after_reservation(
    client: TestClient, make_couple: MakeCouple
) -> None:
    mila, sasha = make_couple()
    wish = add(client, mila)
    before = client.get(ME, headers=mila).json()
    client.post(f"{PARTNER}/{wish['id']}/reserve", headers=sasha)
    after = client.get(ME, headers=mila).json()
    assert before == after


def test_cannot_reserve_received(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    wish = add(client, mila)
    received = client.post(f"{ME}/{wish['id']}/received", headers=mila).json()
    assert received["is_received"] is True and received["received_at"] is not None
    assert client.post(f"{PARTNER}/{wish['id']}/reserve", headers=sasha).status_code == 409

    back = client.delete(f"{ME}/{wish['id']}/received", headers=mila).json()
    assert back["is_received"] is False and back["received_at"] is None


def test_partner_cannot_edit(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    wish = add(client, mila)
    assert client.patch(f"{ME}/{wish['id']}", headers=sasha, json={"title": "x"}).status_code == 404
    assert client.delete(f"{ME}/{wish['id']}", headers=sasha).status_code == 404


def test_update_and_delete(client: TestClient, make_user: Callable[[str], Headers]) -> None:
    mila = make_user("Mila")
    wish = add(client, mila, price=500)
    updated = client.patch(f"{ME}/{wish['id']}", headers=mila, json={"price": 5000}).json()
    assert updated["price"] == 5000 and updated["budget"] == "medium" and updated["title"] == "Пазл"
    assert (
        client.patch(f"{ME}/{wish['id']}", headers=mila, json={"priority": None}).status_code == 422
    )
    assert client.delete(f"{ME}/{wish['id']}", headers=mila).status_code == 204
    assert client.get(ME, headers=mila).json() == []


def test_order(client: TestClient, make_user: Callable[[str], Headers]) -> None:
    mila = make_user("Mila")
    add(client, mila, title="Мелочь", priority="maybe")
    add(client, mila, title="Огонь", priority="burning")
    got = add(client, mila, title="Уже есть", priority="burning")
    add(client, mila, title="Классно", priority="nice")
    client.post(f"{ME}/{got['id']}/received", headers=mila)

    titles = [w["title"] for w in client.get(ME, headers=mila).json()]
    assert titles == ["Огонь", "Классно", "Мелочь", "Уже есть"]
    assert [
        w["title"] for w in client.get(ME, headers=mila, params={"is_received": True}).json()
    ] == ["Уже есть"]


def test_wishlist_without_partner(client: TestClient, make_user: Callable[[str], Headers]) -> None:
    mila = make_user("Mila")
    add(client, mila)  # your own wishlist works even before you have a couple
    assert client.get(PARTNER, headers=mila).status_code == 404
    client.post("/api/v1/couple", headers=mila, json={})
    assert client.get(PARTNER, headers=mila).status_code == 404  # couple, but nobody joined yet


def test_strangers_see_nothing(
    client: TestClient, make_couple: MakeCouple, make_user: Callable[[str], Headers]
) -> None:
    mila, _ = make_couple()
    wish = add(client, mila)
    stranger = make_user("Stranger")
    assert client.post(f"{PARTNER}/{wish['id']}/reserve", headers=stranger).status_code == 404


def test_leaving_couple_drops_reservations(
    client: TestClient, make_couple: MakeCouple, make_user: Callable[[str], Headers]
) -> None:
    mila, sasha = make_couple()
    wish = add(client, mila)
    client.post(f"{PARTNER}/{wish['id']}/reserve", headers=sasha)
    client.post("/api/v1/couple/leave", headers=sasha)

    # Mila invites someone new — they must see the wish as free.
    code = client.get("/api/v1/couple", headers=mila).json()["invite_code"]
    newcomer = make_user("Newcomer")
    client.post("/api/v1/couple/join", headers=newcomer, json={"invite_code": code})
    assert client.get(PARTNER, headers=newcomer).json()[0]["is_reserved"] is False
