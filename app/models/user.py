from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.couple import Couple


class User(Base):
    """Account: only what is needed to sign in."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Empty until the user creates or joins a couple.
    couple_id: Mapped[int | None] = mapped_column(
        ForeignKey("couples.id", ondelete="SET NULL"), index=True
    )

    profile: Mapped["Profile"] = relationship(back_populates="user", cascade="all, delete-orphan")
    couple: Mapped["Couple | None"] = relationship(back_populates="members")


class Profile(Base):
    """Personal details the partner can see. Everything except name is optional."""

    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    # Basics
    name: Mapped[str] = mapped_column(String(100))
    pet_name: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    birth_date: Mapped[date | None] = mapped_column(Date)

    # For gifts. Sizes are text: "17", "38.5", "US 7", "M" — systems differ.
    ring_size: Mapped[str | None] = mapped_column(String(20))
    shoe_size: Mapped[str | None] = mapped_column(String(20))
    clothing_size_top: Mapped[str | None] = mapped_column(String(20))
    clothing_size_bottom: Mapped[str | None] = mapped_column(String(20))
    favorite_color: Mapped[str | None] = mapped_column(String(50))
    favorite_flowers: Mapped[str | None] = mapped_column(String(200))
    allergies: Mapped[str | None] = mapped_column(Text)

    # Relationship
    how_to_support_me: Mapped[str | None] = mapped_column(Text)
    small_annoyances: Mapped[str | None] = mapped_column(Text)

    # Tastes
    favorite_food: Mapped[str | None] = mapped_column(String(200))
    favorite_drink: Mapped[str | None] = mapped_column(String(200))
    food_dislikes: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="profile")
