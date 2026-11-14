from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.couple import Couple


class Memory(Base):
    """A moment the couple wants to keep: what happened, when, where, with photos."""

    __tablename__ = "memories"

    id: Mapped[int] = mapped_column(primary_key=True)
    couple_id: Mapped[int] = mapped_column(ForeignKey("couples.id", ondelete="CASCADE"), index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    # Set when the memory was made from a done idea. One idea -> at most one memory.
    idea_id: Mapped[int | None] = mapped_column(
        ForeignKey("ideas.id", ondelete="SET NULL"), unique=True
    )

    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    happened_on: Mapped[date] = mapped_column(Date)
    place: Mapped[str | None] = mapped_column(String(200))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    couple: Mapped["Couple"] = relationship(back_populates="memories")
    photos: Mapped[list["MemoryPhoto"]] = relationship(
        back_populates="memory",
        cascade="all, delete-orphan",
        order_by="MemoryPhoto.id",
        lazy="selectin",
    )


class MemoryPhoto(Base):
    """A photo file on disk. The database keeps only its random file name."""

    __tablename__ = "memory_photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    memory_id: Mapped[int] = mapped_column(
        ForeignKey("memories.id", ondelete="CASCADE"), index=True
    )
    filename: Mapped[str] = mapped_column(String(100), unique=True)
    content_type: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    memory: Mapped[Memory] = relationship(back_populates="photos")
