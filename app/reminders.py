"""Daily reminders. Run once a day (e.g. at 9:00) on the server:

    uv run python -m app.reminders

Running it twice on the same day is safe: every reminder has a dedupe key,
so nobody gets the same reminder twice.
"""

import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import notifications, push
from app.database import SessionLocal
from app.enums import NotificationType
from app.models import Couple, Memory, Notification, Task, User

log = logging.getLogger(__name__)

BIRTHDAY_DAYS_BEFORE = (7, 1, 0)
ANNIVERSARY_DAYS_BEFORE = (7, 0)
MILESTONE_DAYS = (100, 200, 300, 500, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 10000)


def plural(n: int, one: str, few: str, many: str) -> str:
    """Russian plural: 1 задача, 2 задачи, 5 задач."""
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def next_yearly(day: date, today: date) -> date:
    """The next time this day-of-year comes, today included. 29 Feb -> 28 Feb in other years."""
    for year in (today.year, today.year + 1):
        try:
            candidate = day.replace(year=year)
        except ValueError:
            candidate = date(year, 2, 28)
        if candidate >= today:
            return candidate
    raise AssertionError("unreachable")


def birthday_reminders(db: Session, user: User, partner: User, today: date) -> list[Notification]:
    born = partner.profile.birth_date
    if born is None:
        return []
    birthday = next_yearly(born, today)
    days = (birthday - today).days
    if days not in BIRTHDAY_DAYS_BEFORE:
        return []
    name = partner.profile.name
    title = {
        7: f"Через неделю день рождения у {name}",
        1: f"Завтра день рождения у {name}",
        0: f"Сегодня день рождения у {name}!",
    }[days]
    body = "Загляни в вишлист — там есть идеи" if days else "Не забудь поздравить"
    created = notifications.create(
        db,
        user.id,
        NotificationType.BIRTHDAY,
        title,
        body,
        data={"screen": "wishlist_partner"},
        dedupe_key=f"birthday:{partner.id}:{birthday.isoformat()}:{days}",
    )
    return [created] if created else []


def anniversary_reminders(
    db: Session, user: User, couple: Couple, today: date
) -> list[Notification]:
    since = couple.together_since
    if since is None or since > today:
        return []
    result = []

    anniversary = next_yearly(since, today)
    days = (anniversary - today).days
    years = anniversary.year - since.year
    if years > 0 and days in ANNIVERSARY_DAYS_BEFORE:
        word = plural(years, "год", "года", "лет")
        title = f"Через неделю {years} {word} вместе" if days else f"Сегодня {years} {word} вместе!"
        body = "Время придумать что-то особенное" if days else "С годовщиной!"
        result.append(
            notifications.create(
                db,
                user.id,
                NotificationType.ANNIVERSARY,
                title,
                body,
                data={"screen": "couple"},
                dedupe_key=f"anniversary:{anniversary.isoformat()}:{days}",
            )
        )

    together = (today - since).days
    if together in MILESTONE_DAYS:
        result.append(
            notifications.create(
                db,
                user.id,
                NotificationType.ANNIVERSARY,
                f"Вы вместе уже {together} дней!",
                "Отличный повод для свидания — нажми «Подкинь идею»",
                data={"screen": "suggest"},
                dedupe_key=f"milestone:{together}",
            )
        )
    return [n for n in result if n]


def task_reminders(db: Session, user: User, couple: Couple, today: date) -> list[Notification]:
    tasks = list(
        db.scalars(
            select(Task).where(
                Task.couple_id == couple.id,
                Task.is_done.is_(False),
                Task.due_date <= today,
                (Task.assignee_id == user.id) | Task.assignee_id.is_(None),
            )
        )
    )
    if not tasks:
        return []
    due_today = [t for t in tasks if t.due_date == today]
    overdue = [t for t in tasks if t.due_date < today]
    parts = []
    if due_today:
        parts.append(
            f"{len(due_today)} {plural(len(due_today), 'задача', 'задачи', 'задач')} на сегодня"
        )
    if overdue:
        parts.append(
            f"{len(overdue)} {plural(len(overdue), 'просроченная', 'просроченные', 'просроченных')}"
        )
    titles = ", ".join(f"«{t.title}»" for t in (due_today + overdue)[:3])
    created = notifications.create(
        db,
        user.id,
        NotificationType.TASKS_TODAY,
        ", ".join(parts),
        titles,
        data={"screen": "tasks"},
        dedupe_key=f"tasks:{today.isoformat()}",
    )
    return [created] if created else []


def on_this_day_reminders(
    db: Session, user: User, couple: Couple, today: date
) -> list[Notification]:
    memories = [
        m
        for m in db.scalars(select(Memory).where(Memory.couple_id == couple.id))
        if (m.happened_on.month, m.happened_on.day) == (today.month, today.day)
        and m.happened_on.year < today.year
    ]
    if not memories:
        return []
    oldest = min(memories, key=lambda m: m.happened_on)
    years = today.year - oldest.happened_on.year
    title = (
        "В этот день год назад"
        if years == 1
        else f"В этот день {years} {plural(years, 'год', 'года', 'лет')} назад"
    )
    created = notifications.create(
        db,
        user.id,
        NotificationType.ON_THIS_DAY,
        title,
        f"«{oldest.title}»",
        data={"screen": "on_this_day", "memory_id": oldest.id},
        dedupe_key=f"on_this_day:{today.isoformat()}",
    )
    return [created] if created else []


def run(db: Session, today: date | None = None) -> list[Notification]:
    """Create today's reminders for everyone, send pushes, return what was created."""
    today = today or date.today()
    created: list[Notification] = []
    for couple in db.scalars(select(Couple)):
        for user in couple.members:
            partner = user.partner
            if partner is not None:
                created += birthday_reminders(db, user, partner, today)
                created += anniversary_reminders(db, user, couple, today)
            created += task_reminders(db, user, couple, today)
            created += on_this_day_reminders(db, user, couple, today)
    db.commit()

    messages = [m for n in created for m in notifications.push_messages_for(db, n)]
    if messages:
        push.send_messages(messages)
    return created


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    with SessionLocal() as db:
        created = run(db)
    log.info("Created %d reminders", len(created))


if __name__ == "__main__":
    main()
