from collections.abc import Callable

from fastapi.testclient import TestClient

from app.love_language import QUESTIONS

URL = "/api/v1/love-language"
Headers = dict[str, str]
MakeCouple = Callable[[], tuple[Headers, Headers]]


def answers_for(favourites: dict[str, int], default: int = 1) -> dict[str, int]:
    """Rate every statement of a language the same: {"time": 5} -> all TIME statements get 5."""
    return {str(q.id): favourites.get(q.language.value, default) for q in QUESTIONS}


def test_questions_hide_languages(client: TestClient) -> None:
    test = client.get(f"{URL}/test").json()
    assert len(test["questions"]) == 20
    assert set(test["questions"][0]) == {"id", "text"}


def test_one_clear_language(client: TestClient, make_user: Callable[[str], Headers]) -> None:
    mila = make_user("Mila")
    result = client.post(
        f"{URL}/test", headers=mila, json={"answers": answers_for({"time": 5, "touch": 3})}
    ).json()
    assert result["leading"] == ["time"]
    assert result["scores"][0] == {"language": "time", "title": "Время вместе", "percent": 100}
    assert result["scores"][1]["language"] == "touch" and result["scores"][1]["percent"] == 50
    assert result["scores"][-1]["percent"] == 0
    assert [t["language"] for t in result["tips"]] == ["time"]
    assert result["tips"][0]["how_to_show"]


def test_several_leading_languages(client: TestClient, make_user: Callable[[str], Headers]) -> None:
    mila = make_user("Mila")
    answers = answers_for({"words": 5, "gifts": 5, "service": 2})
    answers["1"] = 4  # one WORDS statement a bit lower: 95 % — still within 10 % of the top
    result = client.post(f"{URL}/test", headers=mila, json={"answers": answers}).json()
    assert result["leading"] == ["gifts", "words"]


def test_validation(client: TestClient, make_user: Callable[[str], Headers]) -> None:
    mila = make_user("Mila")
    missing = answers_for({})
    del missing["20"]
    assert client.post(f"{URL}/test", headers=mila, json={"answers": missing}).status_code == 422
    too_high = answers_for({}, default=6)
    assert client.post(f"{URL}/test", headers=mila, json={"answers": too_high}).status_code == 422
    extra = {**answers_for({}), "99": 3}
    assert client.post(f"{URL}/test", headers=mila, json={"answers": extra}).status_code == 422


def test_retake_replaces_result(client: TestClient, make_user: Callable[[str], Headers]) -> None:
    mila = make_user("Mila")
    assert client.get(f"{URL}/me", headers=mila).status_code == 404
    client.post(f"{URL}/test", headers=mila, json={"answers": answers_for({"words": 5})})
    client.post(f"{URL}/test", headers=mila, json={"answers": answers_for({"touch": 5})})
    assert client.get(f"{URL}/me", headers=mila).json()["leading"] == ["touch"]


def test_partner_result(
    client: TestClient, make_couple: MakeCouple, make_user: Callable[[str], Headers]
) -> None:
    mila, sasha = make_couple()
    assert client.get(f"{URL}/partner", headers=mila).status_code == 404  # not taken yet
    client.post(f"{URL}/test", headers=sasha, json={"answers": answers_for({"service": 5})})
    partner = client.get(f"{URL}/partner", headers=mila).json()
    assert partner["leading"] == ["service"]
    assert "ужин" in partner["tips"][0]["how_to_show"]

    assert client.get(f"{URL}/partner", headers=make_user("Single")).status_code == 404
