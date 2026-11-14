"""Creating notifications: one place used by every section of the app.

A notification is always saved to the recipient's list (the "bell").
A push to their phone is sent only if they have a phone registered and
haven't switched that category off in settings.

Never notify about secret things: gift reservations and gift notes.
"""

from fastapi import BackgroundTasks
from sqlalchemy import select

from app import push
from app.enums import NotificationCategory, NotificationType
from app.models import Device, Notification, NotificationSettings, User

T, C = NotificationType, NotificationCategory

CATEGORY_OF: dict[NotificationType, NotificationCategory] = {
    T.PARTNER_JOINED: C.COUPLE,
    T.TASK_ADDED: C.TASKS,
    T.TASK_ASSIGNED: C.TASKS,
    T.TASK_DONE: C.TASKS,
    T.IDEA_ADDED: C.IDEAS,
    T.IDEA_WANTED: C.IDEAS,
    T.MEMORY_ADDED: C.MEMORIES,
    T.PHOTOS_ADDED: C.MEMORIES,
    T.WISH_ADDED: C.WISHLIST,
    T.LOVE_LANGUAGE_DONE: C.LOVE_LANGUAGE,
    T.BIRTHDAY: C.BIRTHDAY,
    T.ANNIVERSARY: C.ANNIVERSARY,
    T.TASKS_TODAY: C.TASKS_DUE,
    T.ON_THIS_DAY: C.ON_THIS_DAY,
}
assert set(CATEGORY_OF) == set(NotificationType), "every notification type needs a category"


def muted_categories(db, user_id: int) -> set[str]:
    row = db.scalar(select(NotificationSettings).where(NotificationSettings.user_id == user_id))
    return set(row.muted) if row else set()


def push_messages_for(db, notification: Notification) -> list[dict]:
    """The push messages for this notification, or [] if push is off for it."""
    if CATEGORY_OF[notification.type] in muted_categories(db, notification.user_id):
        return []
    tokens = db.scalars(select(Device.push_token).where(Device.user_id == notification.user_id))
    return [
        {
            "to": token,
            "title": notification.title,
            "body": notification.body,
            "data": {**notification.data, "notification_id": notification.id},
            "sound": "default",
        }
        for token in tokens
    ]


def create(
    db,
    recipient_id: int,
    type: NotificationType,
    title: str,
    body: str,
    *,
    data: dict | None = None,
    actor: User | None = None,
    dedupe_key: str | None = None,
) -> Notification | None:
    """Add a notification to the session. Returns None if this dedupe_key already exists."""
    if dedupe_key is not None:
        exists = db.scalar(
            select(Notification.id).where(
                Notification.user_id == recipient_id, Notification.dedupe_key == dedupe_key
            )
        )
        if exists is not None:
            return None
    notification = Notification(
        user_id=recipient_id,
        actor_id=actor.id if actor else None,
        type=type,
        title=title,
        body=body,
        data=data or {},
        dedupe_key=dedupe_key,
    )
    db.add(notification)
    db.flush()  # gives it an id now, for the push data
    return notification


def notify_partner(
    db,
    background: BackgroundTasks,
    actor: User,
    type: NotificationType,
    title: str,
    what: str,
    data: dict | None = None,
) -> None:
    """Tell the actor's partner what the actor just did: "Саша: «Купить продукты»".

    Call it before db.commit(); the push itself goes out after the response is sent.
    """
    partner = actor.partner
    if partner is None:
        return
    notification = create(
        db, partner.id, type, title, f"{actor.profile.name}: {what}", data=data, actor=actor
    )
    if notification is not None:
        messages = push_messages_for(db, notification)
        if messages:
            background.add_task(push.send_messages, messages)
