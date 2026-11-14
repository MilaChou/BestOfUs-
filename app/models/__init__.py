"""Database models.

Import every model here so Alembic sees all tables when it
autogenerates migrations.
"""

from app.database import Base
from app.models.couple import Couple
from app.models.idea import Idea, IdeaWant
from app.models.user import Profile, User
from app.models.wish import GiftNote, Wish

__all__ = ["Base", "Couple", "GiftNote", "Idea", "IdeaWant", "Profile", "User", "Wish"]
