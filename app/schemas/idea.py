from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from app.enums import Budget, Cuisine, Format, TimeOfDay


def _unique_sorted(times: list[TimeOfDay] | None) -> list[TimeOfDay] | None:
    """["evening", "morning", "evening"] -> ["morning", "evening"]."""
    if times is None:
        return None
    return sorted(set(times), key=list(TimeOfDay).index)


class IdeaCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    link: str | None = Field(default=None, max_length=500)
    format: Format
    cuisine: Cuisine | None = None
    budget: Budget | None = None
    times_of_day: list[TimeOfDay] = Field(
        default_factory=list, description="Empty list means any time of day."
    )

    _normalize_times = field_validator("times_of_day")(_unique_sorted)

    @model_validator(mode="after")
    def cuisine_only_for_food(self) -> "IdeaCreate":
        if self.cuisine is not None and self.format != Format.FOOD:
            raise ValueError("cuisine can be set only when format is 'food'")
        return self


class IdeaUpdate(BaseModel):
    """Only the fields that are sent get changed."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    link: str | None = Field(default=None, max_length=500)
    format: Format = None
    cuisine: Cuisine | None = None
    budget: Budget | None = None
    times_of_day: list[TimeOfDay] = None

    _normalize_times = field_validator("times_of_day")(_unique_sorted)


class IdeaDone(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    review: str | None = Field(default=None, max_length=2000)


class IdeaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    link: str | None
    format: Format
    cuisine: Cuisine | None
    budget: Budget | None
    times_of_day: list[TimeOfDay]
    author_id: int | None
    wanted_by: list[int]
    is_done: bool
    done_at: datetime | None
    rating: int | None
    review: str | None
    catalog_id: str | None
    created_at: datetime

    @computed_field
    @property
    def both_want(self) -> bool:
        return len(self.wanted_by) >= 2


class CatalogActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    format: Format
    cuisine: Cuisine | None
    budget: Budget
    times_of_day: list[TimeOfDay]


class Suggestion(BaseModel):
    """Result of "Подкинь идею": either one of the couple's ideas or a catalog activity."""

    source: Literal["idea", "catalog"]
    idea: IdeaRead | None = None
    activity: CatalogActivityRead | None = None
