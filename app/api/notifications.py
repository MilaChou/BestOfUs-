from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import delete, func, select, update

from app.api.deps import CurrentUser
from app.database import DbSession
from app.enums import NotificationCategory
from app.models import Device, Notification, NotificationSettings
from app.notifications import muted_categories
from app.schemas.notification import (
    DeviceRegister,
    DeviceRemove,
    NotificationRead,
    SettingsRead,
    SettingsUpdate,
    UnreadCount,
)

router = APIRouter(tags=["notifications"])


# --- The bell --------------------------------------------------------------


@router.get("/notifications", response_model=list[NotificationRead])
def list_notifications(
    user: CurrentUser,
    db: DbSession,
    unread_only: bool = False,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[Notification]:
    """Newest first. Use limit/offset to load more while scrolling."""
    stmt = select(Notification).where(Notification.user_id == user.id)
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    stmt = stmt.order_by(Notification.created_at.desc(), Notification.id.desc())
    return list(db.scalars(stmt.limit(limit).offset(offset)))


@router.get("/notifications/unread-count", response_model=UnreadCount)
def unread_count(user: CurrentUser, db: DbSession) -> UnreadCount:
    """The number on the bell icon."""
    count = db.scalar(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user.id, Notification.is_read.is_(False))
    )
    return UnreadCount(unread=count or 0)


@router.post("/notifications/read-all", status_code=status.HTTP_204_NO_CONTENT)
def read_all(user: CurrentUser, db: DbSession) -> None:
    db.execute(
        update(Notification)
        .where(Notification.user_id == user.id, Notification.is_read.is_(False))
        .values(is_read=True, read_at=datetime.now(UTC))
    )
    db.commit()


@router.post("/notifications/{notification_id}/read", response_model=NotificationRead)
def read_one(notification_id: int, user: CurrentUser, db: DbSession) -> Notification:
    notification = db.get(Notification, notification_id)
    if notification is None or notification.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = datetime.now(UTC)
        db.commit()
        db.refresh(notification)
    return notification


# --- Settings --------------------------------------------------------------


def settings_row(user_id: int, db: DbSession) -> NotificationSettings:
    row = db.scalar(select(NotificationSettings).where(NotificationSettings.user_id == user_id))
    if row is None:
        row = NotificationSettings(user_id=user_id, muted=[])
        db.add(row)
    return row


@router.get("/notifications/settings", response_model=SettingsRead)
def get_settings(user: CurrentUser, db: DbSession) -> SettingsRead:
    """Which pushes are on. Switched-off ones still appear in the list, just without a push."""
    muted = muted_categories(db, user.id)
    return {category: category.value not in muted for category in NotificationCategory}


@router.patch("/notifications/settings", response_model=SettingsRead)
def update_settings(data: SettingsUpdate, user: CurrentUser, db: DbSession) -> SettingsRead:
    """Send only what changes, e.g. {"birthday": false}."""
    row = settings_row(user.id, db)
    muted = set(row.muted)
    for category, enabled in data.items():
        if enabled:
            muted.discard(category.value)
        else:
            muted.add(category.value)
    row.muted = sorted(muted)  # a new list, so SQLAlchemy notices the change
    db.commit()
    return {category: category.value not in muted for category in NotificationCategory}


# --- Phones ----------------------------------------------------------------


@router.post("/devices", status_code=status.HTTP_204_NO_CONTENT)
def register_device(data: DeviceRegister, user: CurrentUser, db: DbSession) -> None:
    """The app calls this after login with its Expo push token.

    If the same phone was used by another account before, it now belongs to this one.
    """
    device = db.scalar(select(Device).where(Device.push_token == data.push_token))
    if device is None:
        db.add(Device(user_id=user.id, push_token=data.push_token, platform=data.platform))
    else:
        device.user_id = user.id
        device.platform = data.platform
    db.commit()


@router.delete("/devices", status_code=status.HTTP_204_NO_CONTENT)
def remove_device(data: DeviceRemove, user: CurrentUser, db: DbSession) -> None:
    """The app calls this on logout, so the phone stops getting pushes."""
    db.execute(
        delete(Device).where(Device.user_id == user.id, Device.push_token == data.push_token)
    )
    db.commit()
