"""Database models.

Import every model here so Alembic sees all tables when it
autogenerates migrations.
"""

from app.database import Base
from app.models.couple import Couple
from app.models.idea import Idea, IdeaWant
from app.models.memory import Memory, MemoryPhoto
from app.models.notification import Device, Notification, NotificationSettings
from app.models.task import Task
from app.models.test_result import TestResult
from app.models.user import Profile, User
from app.models.wish import GiftNote, Wish

__all__ = [
    "Base",
    "Couple",
    "Device",
    "GiftNote",
    "Idea",
    "IdeaWant",
    "Memory",
    "MemoryPhoto",
    "Notification",
    "NotificationSettings",
    "Profile",
    "Task",
    "TestResult",
    "User",
    "Wish",
]
