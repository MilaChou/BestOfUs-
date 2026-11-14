from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LoveLanguageResult(Base):
    """The latest love language test result of one person. Retaking replaces it."""

    __tablename__ = "love_language_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    # {"words": 75, "time": 100, ...} — percent per language.
    scores: Mapped[dict[str, int]] = mapped_column(JSON)
    taken_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
