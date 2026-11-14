from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.enums import TaskCategory


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    note: str | None = Field(default=None, max_length=2000)
    category: TaskCategory | None = None
    due_date: date | None = None
    assignee_id: int | None = Field(default=None, description="Empty = both of us.")


class TaskUpdate(BaseModel):
    """Only the fields that are sent get changed."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(default=None, min_length=1, max_length=200)
    note: str | None = Field(default=None, max_length=2000)
    category: TaskCategory | None = None
    due_date: date | None = None
    assignee_id: int | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    note: str | None
    category: TaskCategory | None
    due_date: date | None
    author_id: int | None
    assignee_id: int | None
    is_done: bool
    done_at: datetime | None
    done_by_id: int | None
    created_at: datetime

    @computed_field
    @property
    def is_overdue(self) -> bool:
        return not self.is_done and self.due_date is not None and self.due_date < date.today()
