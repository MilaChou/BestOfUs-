from collections.abc import Callable
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import reminders
from app.reminders import next_yearly, plural

Headers = dict[str, str]
MakeCouple = Callable[[], tuple[Headers, Headers]]
API = "/api/v1"
TODAY = date(2026, 11, 13)


def bell(client: TestClient, headers: Headers) -> list[dict]:
    return client.get(f"{API}/notifications", headers=headers).json()


def titles(client: TestClient, headers: Headers) -> list[str]:
    return [n["title"] for n in bell(client, headers)]


def test_plural() -> None:
    words = [plural(n, "задача", "задачи", "задач") for n in (1, 2, 5, 11, 12, 21, 22, 25, 111)]
    assert words == [
        "задача",
        "задачи",
        "задач",
        "задач",
        "задач",
        "задача",
        "задачи",
        "задач",
        "задач",
    ]


def test_next_yearly() -> None:
    assert next_yearly(date(1999, 11, 20), TODAY) == date(2026, 11, 20)
    assert next_yearly(date(1999, 11, 13), TODAY) == TODAY
    assert next_yearly(date(1999, 1, 5), TODAY) == date(2027, 1, 5)
    assert next_yearly(date(2000, 2, 29), date(2027, 2, 1)) == date(2027, 2, 28)


def test_birthday(
    client: TestClient, db_session: Session, make_couple: MakeCouple, pushed: list
) -> None:
    mila, sasha = make_couple()
    client.patch(f"{API}/users/me/profile", headers=sasha, json={"birth_date": "1999-11-20"})
    client.post(
        f"{API}/devices",
        headers=mila,
        json={"push_token": "ExponentPushToken[mila]", "platform": "ios"},
    )

    reminders.run(db_session, date(2026, 11, 13))
    assert titles(client, mila)[0] == "🎂 Через неделю день рождения у Sasha"
    assert pushed[-1]["title"] == "🎂 Через неделю день рождения у Sasha"
    assert all("день рождения" not in t for t in titles(client, sasha))  # not about yourself

    reminders.run(db_session, date(2026, 11, 13))  # a second run the same day changes nothing
    assert sum("день рождения" in t for t in titles(client, mila)) == 1

    reminders.run(db_session, date(2026, 11, 14))  # 6 days before: nothing
    reminders.run(db_session, date(2026, 11, 19))
    reminders.run(db_session, date(2026, 11, 20))
    assert titles(client, mila)[:2] == [
        "🎉 Сегодня день рождения у Sasha!",
        "🎂 Завтра день рождения у Sasha",
    ]


def test_anniversary_and_milestones(
    client: TestClient, db_session: Session, make_couple: MakeCouple
) -> None:
    mila, sasha = make_couple()
    client.patch(f"{API}/couple", headers=mila, json={"together_since": "2024-11-20"})

    reminders.run(db_session, date(2026, 11, 13))
    assert titles(client, mila)[0] == "💍 Через неделю 2 года вместе"
    reminders.run(db_session, date(2026, 11, 20))
    assert titles(client, sasha)[0] == "💍 Сегодня 2 года вместе!"

    reminders.run(db_session, date(2027, 8, 17))  # 1000 days after 2024-11-20
    assert titles(client, mila)[0] == "✨ Вы вместе уже 1000 дней!"


def test_tasks_today(client: TestClient, db_session: Session, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    sasha_id = client.get(f"{API}/users/me", headers=sasha).json()["id"]
    client.post(
        f"{API}/couple/tasks", headers=mila, json={"title": "Общая", "due_date": "2026-11-13"}
    )
    client.post(
        f"{API}/couple/tasks",
        headers=mila,
        json={"title": "Сашина", "due_date": "2026-11-13", "assignee_id": sasha_id},
    )
    client.post(
        f"{API}/couple/tasks", headers=mila, json={"title": "Старая", "due_date": "2026-11-01"}
    )
    client.post(
        f"{API}/couple/tasks", headers=mila, json={"title": "Потом", "due_date": "2026-12-01"}
    )

    reminders.run(db_session, TODAY)
    mila_note = next(n for n in bell(client, mila) if n["type"] == "tasks_today")
    sasha_note = next(n for n in bell(client, sasha) if n["type"] == "tasks_today")
    assert mila_note["title"] == "📋 1 задача на сегодня, 1 просроченная"
    assert sasha_note["title"] == "📋 2 задачи на сегодня, 1 просроченная"
    assert "«Потом»" not in sasha_note["body"]


def test_on_this_day(client: TestClient, db_session: Session, make_couple: MakeCouple) -> None:
    mila, sasha = make_couple()
    client.post(
        f"{API}/couple/memories",
        headers=mila,
        json={"title": "Первое свидание", "happened_on": "2023-11-13"},
    )
    client.post(
        f"{API}/couple/memories",
        headers=mila,
        json={"title": "Сегодняшнее", "happened_on": "2026-11-13"},
    )
    reminders.run(db_session, TODAY)
    note = next(n for n in bell(client, sasha) if n["type"] == "on_this_day")
    assert note["title"] == "📸 В этот день 3 года назад" and note["body"] == "«Первое свидание»"


def test_nothing_to_remind(
    client: TestClient, db_session: Session, make_couple: MakeCouple
) -> None:
    make_couple()
    assert [n for n in reminders.run(db_session, TODAY) if n.type != "partner_joined"] == []
