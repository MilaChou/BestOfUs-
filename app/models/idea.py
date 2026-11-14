from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import Budget, Cuisine, Format

if TYPE_CHECKING:
    from app.models.couple import Couple


def enum_column(enum: type[StrEnum]) -> Enum:
    """Store an enum as its plain text value ("food"), not as a database-specific type."""
    return Enum(
        enum,
        native_enum=False,
        length=20,
        values_callable=lambda members: [m.value for m in members],
    )


class Idea(Base):
    """Something the couple wants to do together some day."""

    __tablename__ = "ideas"

    id: Mapped[int] = mapped_column(primary_key=True)
    couple_id: Mapped[int] = mapped_column(ForeignKey("couples.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    link: Mapped[str | None] = mapped_column(String(500))

    # Tags used by filters and by "Подкинь идею".
    format: Mapped[Format] = mapped_column(enum_column(Format))
    cuisine: Mapped[Cuisine | None] = mapped_column(enum_column(Cuisine))  # only for food
    budget: Mapped[Budget | None] = mapped_column(enum_column(Budget))  # empty = not decided
    times_of_day: Mapped[list[str]] = mapped_column(JSON, default=list)  # empty = any time

    # Set when the idea was saved from the activity catalog.
    catalog_id: Mapped[str | None] = mapped_column(String(50))

    is_done: Mapped[bool] = mapped_column(default=False)
    done_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rating: Mapped[int | None] = mapped_column(SmallInteger)  # 1–5 after it's done
    review: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    couple: Mapped["Couple"] = relationship(back_populates="ideas")
    wants: Mapped[list["IdeaWant"]] = relationship(
        back_populates="idea", cascade="all, delete-orphan", lazy="selectin"
    )

    @property
    def wanted_by(self) -> list[int]:
        """Ids of members who pressed "Хочу тоже!" ❤️."""
        return sorted(want.user_id for want in self.wants)


class IdeaWant(Base):
    """One member's ❤️ on an idea. The pair (idea, user) is the key, so it can't repeat."""

    __tablename__ = "idea_wants"

    idea_id: Mapped[int] = mapped_column(
        ForeignKey("ideas.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    idea: Mapped[Idea] = relationship(back_populates="wants")
