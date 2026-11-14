from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.config import settings


class MemoryCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    happened_on: date = Field(default_factory=date.today)
    place: str | None = Field(default=None, max_length=200)


class MemoryUpdate(BaseModel):
    """Only the fields that are sent get changed."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    happened_on: date = None
    place: str | None = Field(default=None, max_length=200)


class PhotoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    memory_id: int
    content_type: str

    @computed_field
    @property
    def url(self) -> str:
        """Open it with the same Authorization header as any other request."""
        return f"{settings.api_prefix}/couple/memories/{self.memory_id}/photos/{self.id}"


class MemoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    happened_on: date
    place: str | None
    author_id: int | None
    idea_id: int | None
    photos: list[PhotoRead]
    created_at: datetime

    @computed_field
    @property
    def years_ago(self) -> int:
        """For "В этот день": 0 this year, 1 a year ago, ..."""
        return date.today().year - self.happened_on.year
