from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums import DevicePlatform, NotificationCategory, NotificationType


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: NotificationType
    title: str
    body: str
    data: dict
    actor_id: int | None
    is_read: bool
    read_at: datetime | None
    created_at: datetime


class UnreadCount(BaseModel):
    unread: int


class DeviceRegister(BaseModel):
    push_token: str = Field(min_length=1, max_length=255, examples=["ExponentPushToken[xxxxxxxx]"])
    platform: DevicePlatform


class DeviceRemove(BaseModel):
    push_token: str = Field(min_length=1, max_length=255)


# {"tasks": true, "birthday": false, ...} — every category, on or off.
SettingsRead = dict[NotificationCategory, bool]
SettingsUpdate = dict[NotificationCategory, bool]
