from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import TaskCategory
from app.models.idea import enum_column

if TYPE_CHECKING:
    from app.models.couple import Couple


class Task(Base):
    """An everyday to-do of the couple: «купить продукты», «записаться к врачу»."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    couple_id: Mapped[int] = mapped_column(ForeignKey("couples.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    # Who should do it. Empty = both of us.
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    title: Mapped[str] = mapped_column(String(200))
    note: Mapped[str | None] = mapped_column(Text)
    category: Mapped[TaskCategory | None] = mapped_column(enum_column(TaskCategory))
    due_date: Mapped[date | None] = mapped_column(Date)

    is_done: Mapped[bool] = mapped_column(default=False)
    done_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    done_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    couple: Mapped["Couple"] = relationship(back_populates="tasks")
