from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """What the client sends to register."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=100)


class ProfileUpdate(BaseModel):
    """Profile fields the user can edit. Only the fields that are sent get changed."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(default=None, min_length=1, max_length=100)
    pet_name: str | None = Field(default=None, max_length=100)
    avatar_url: str | None = Field(default=None, max_length=500)
    birth_date: date | None = None
    ring_size: str | None = Field(default=None, max_length=20)
    shoe_size: str | None = Field(default=None, max_length=20)
    clothing_size_top: str | None = Field(default=None, max_length=20)
    clothing_size_bottom: str | None = Field(default=None, max_length=20)
    favorite_color: str | None = Field(default=None, max_length=50)
    favorite_flowers: str | None = Field(default=None, max_length=200)
    allergies: str | None = Field(default=None, max_length=2000)
    how_to_support_me: str | None = Field(default=None, max_length=2000)
    small_annoyances: str | None = Field(default=None, max_length=2000)
    favorite_food: str | None = Field(default=None, max_length=200)
    favorite_drink: str | None = Field(default=None, max_length=200)
    food_dislikes: str | None = Field(default=None, max_length=2000)


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    pet_name: str | None
    avatar_url: str | None
    birth_date: date | None
    ring_size: str | None
    shoe_size: str | None
    clothing_size_top: str | None
    clothing_size_bottom: str | None
    favorite_color: str | None
    favorite_flowers: str | None
    allergies: str | None
    how_to_support_me: str | None
    small_annoyances: str | None
    favorite_food: str | None
    favorite_drink: str | None
    food_dislikes: str | None


class UserRead(BaseModel):
    """What the API returns. Never includes the password."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime
    profile: ProfileRead


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
