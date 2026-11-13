"""Database models.

Import every model here so Alembic sees all tables when it
autogenerates migrations.
"""

from app.database import Base
from app.models.user import Profile, User

__all__ = ["Base", "Profile", "User"]
