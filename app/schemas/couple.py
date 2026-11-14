from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.schemas.user import ProfileRead


class CoupleCreate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    together_since: date | None = None


class CoupleUpdate(BaseModel):
    """Only the fields that are sent get changed."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, max_length=100)
    together_since: date | None = None


class CoupleJoin(BaseModel):
    invite_code: str = Field(min_length=1, max_length=20)


class MemberRead(BaseModel):
    """A member as seen by the couple: the partner sees the whole profile."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    profile: ProfileRead


class CoupleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str | None
    together_since: date | None
    invite_code: str | None
    created_at: datetime
    members: list[MemberRead]

    @computed_field
    @property
    def days_together(self) -> int | None:
        if self.together_since is None:
            return None
        return (date.today() - self.together_since).days
