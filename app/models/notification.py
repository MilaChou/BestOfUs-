from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums import DevicePlatform, NotificationType
from app.models.idea import enum_column


class Notification(Base):
    """One entry in a user's notification list (the "bell")."""

    __tablename__ = "notifications"
    # A daily reminder job may run twice; the key makes the second run a no-op.
    __table_args__ = (UniqueConstraint("user_id", "dedupe_key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # Who caused it (the partner). Empty for scheduled reminders.
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    type: Mapped[NotificationType] = mapped_column(enum_column(NotificationType))
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(String(500))
    # Where the app should go on tap, e.g. {"task_id": 5}.
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    dedupe_key: Mapped[str | None] = mapped_column(String(200))

    is_read: Mapped[bool] = mapped_column(default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Device(Base):
    """A phone that can receive push notifications for a user."""

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # The token the phone got from Expo, e.g. "ExponentPushToken[xxxx]".
    push_token: Mapped[str] = mapped_column(String(255), unique=True)
    platform: Mapped[DevicePlatform] = mapped_column(enum_column(DevicePlatform))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class NotificationSettings(Base):
    """Which notification categories a user turned off. No row = everything on."""

    __tablename__ = "notification_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    muted: Mapped[list[str]] = mapped_column(JSON, default=list)
