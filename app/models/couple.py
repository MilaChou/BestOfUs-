import secrets
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User

MAX_MEMBERS = 2

# No 0/O and 1/I/L, so a code read aloud or typed from a screenshot isn't misread.
INVITE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
INVITE_CODE_LENGTH = 8


def generate_invite_code() -> str:
    return "".join(secrets.choice(INVITE_ALPHABET) for _ in range(INVITE_CODE_LENGTH))


class Couple(Base):
    """Shared space of two people. Everything the pair creates will belong to it."""

    __tablename__ = "couples"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(100))
    together_since: Mapped[date | None] = mapped_column(Date)
    # Set while the couple waits for the second person; cleared once it is full.
    invite_code: Mapped[str | None] = mapped_column(String(INVITE_CODE_LENGTH), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    members: Mapped[list["User"]] = relationship(back_populates="couple", order_by="User.id")

    @property
    def is_full(self) -> bool:
        return len(self.members) >= MAX_MEMBERS
