from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TestResult(Base):
    """A person's latest result of one test ("love", "apology"). Retaking replaces it."""

    __tablename__ = "test_results"
    __table_args__ = (UniqueConstraint("user_id", "test_id"),)
    __test__ = False  # tell pytest this is not a test class despite the name

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    test_id: Mapped[str] = mapped_column(String(30))
    # {"words": 9, "time": 4, ...} — points per category.
    scores: Mapped[dict[str, int]] = mapped_column(JSON)
    taken_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
