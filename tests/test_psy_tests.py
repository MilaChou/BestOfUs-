from collections import Counter
from collections.abc import Callable
from itertools import combinations

import pytest
from fastapi.testclient import TestClient

from app.psy_tests import TESTS, PsyTest

API = "/api/v1/tests"
Headers = dict[str, str]
MakeCouple = Callable[[], tuple[Headers, Headers]]


def choose(test: PsyTest, favourite: str, fallback: str = "a") -> dict[str, str]:
    """Answers that pick `favourite` whenever it is offered."""
    answers = {}
    for q in test.questions:
        if q.a_key == favourite:
            answers[str(q.id)] = "a"
        elif q.b_key == favourite:
            answers[str(q.id)] = "b"
        else:
            answers[str(q.id)] = fallback
    return answers


@pytest.mark.parametrize("test", TESTS.values(), ids=TESTS.keys())
def test_questions_are_balanced(test: PsyTest) -> None:
    """Every category appears equally often and every pair is compared equally often."""
    keys = [c.key for c in test.categories]
    appearances = Counter(k for q in test.questions for k in (q.a_key, q.b_key))
    assert set(appearances.values()) == {test.max_points}
    pairs = Counter(frozenset((q.a_key, q.b_key)) for q in test.questions)
    assert set(pairs) == {frozenset(p) for p in combinations(keys, 2)}
    assert len(set(pairs.values())) == 1
    assert all(q.a_key != q.b_key for q in test.questions)
    texts = [t for q in test.questions for t in (q.a_text, q.b_text)]
    assert len(texts) == len(set(texts)), "every statement is used once"
    assert [q.id for q in test.questions] == list(range(1, len(test.questions) + 1))


def test_list_and_questions_hide_categories(
    client: TestClient, make_user: Callable[[str], Headers]
) -> None:
    mila = make_user("Mila")
    tests = client.get(API, headers=mila).json()
    assert [(t["id"], t["questions_count"]) for t in tests] == [("love", 30), ("apology", 20)]
    assert all(t["my_leading"] == [] for t in tests)

    love = client.get(f"{API}/love").json()
    assert love["prompt"] and len(love["questions"]) == 30
    assert set(love["questions"][0]) == {"id", "a", "b"}
    assert client.get(f"{API}/nope").status_code == 404


@pytest.mark.parametrize("test_id", TESTS.keys())
def test_clear_winner(
    client: TestClient, make_user: Callable[[str], Headers], test_id: str
) -> None:
    test = TESTS[test_id]
    favourite = test.categories[2].key
    mila = make_user("Mila")
    result = client.post(
        f"{API}/{test_id}", headers=mila, json={"answers": choose(test, favourite)}
    ).json()
    assert result["leading"] == [favourite]
    assert result["scores"][0]["key"] == favourite
    assert (
        result["scores"][0]["points"] == test.max_points and result["scores"][0]["percent"] == 100
    )
    assert sum(s["points"] for s in result["scores"]) == len(test.questions)
    assert [a["key"] for a in result["advice"]] == [favourite]


@pytest.mark.parametrize("test_id", TESTS.keys())
def test_side_gives_no_advantage(
    client: TestClient, make_user: Callable[[str], Headers], test_id: str
) -> None:
    """Always pressing "A" favours nobody: every language gets exactly half, none gets 100%."""
    mila = make_user("Mila")
    answers = {str(q.id): "a" for q in TESTS[test_id].questions}
    result = client.post(f"{API}/{test_id}", headers=mila, json={"answers": answers}).json()
    assert {s["percent"] for s in result["scores"]} == {50}


def test_validation(client: TestClient, make_user: Callable[[str], Headers]) -> None:
    mila = make_user("Mila")
    answers = choose(TESTS["apology"], "regret")
    del answers["20"]
    assert client.post(f"{API}/apology", headers=mila, json={"answers": answers}).status_code == 422
    answers["20"] = "c"
    assert client.post(f"{API}/apology", headers=mila, json={"answers": answers}).status_code == 422


def test_retake_and_partner(client: TestClient, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    assert client.get(f"{API}/love/me", headers=mila).status_code == 404
    assert client.get(f"{API}/love/partner", headers=sasha).status_code == 404

    client.post(f"{API}/love", headers=mila, json={"answers": choose(TESTS["love"], "words")})
    client.post(f"{API}/love", headers=mila, json={"answers": choose(TESTS["love"], "touch")})
    assert client.get(f"{API}/love/me", headers=mila).json()["leading"] == ["touch"]

    partner = client.get(f"{API}/love/partner", headers=sasha).json()
    assert partner["leading"] == ["touch"] and partner["advice_title"] == "Как проявлять любовь"
    assert client.get(f"{API}/apology/partner", headers=sasha).status_code == 404

    tests = {t["id"]: t for t in client.get(API, headers=mila).json()}
    assert tests["love"]["my_leading"] == ["Прикосновения"] and tests["apology"]["my_leading"] == []

    bell = client.get("/api/v1/notifications", headers=sasha).json()
    assert bell[0]["title"] == "Язык любви" and bell[0]["data"]["test"] == "love"
