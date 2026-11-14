from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums import GiftType, WishPriority
from app.models.idea import enum_column


class Wish(Base):
    """One item on a person's wishlist. The partner sees it and can secretly reserve it."""

    __tablename__ = "wishes"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    title: Mapped[str] = mapped_column(String(200))
    link: Mapped[str | None] = mapped_column(String(500))
    price: Mapped[int | None] = mapped_column(Integer)  # rubles
    image_url: Mapped[str | None] = mapped_column(String(500))
    note: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[WishPriority] = mapped_column(
        enum_column(WishPriority), default=WishPriority.NICE
    )
    gift_type: Mapped[GiftType | None] = mapped_column(enum_column(GiftType))

    is_received: Mapped[bool] = mapped_column(default=False)
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # "Я подарю". The owner never gets to see these two fields.
    reserved_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    reserved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    @property
    def is_reserved(self) -> bool:
        return self.reserved_by_id is not None


class GiftNote(Base):
    """A secret note "what to gift my partner". Only its author ever sees it."""

    __tablename__ = "gift_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    title: Mapped[str] = mapped_column(String(200))
    note: Mapped[str | None] = mapped_column(Text)
    link: Mapped[str | None] = mapped_column(String(500))
    price: Mapped[int | None] = mapped_column(Integer)
    gift_type: Mapped[GiftType | None] = mapped_column(enum_column(GiftType))
    catalog_id: Mapped[str | None] = mapped_column(String(50))  # saved from the gift catalog
    is_gifted: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
