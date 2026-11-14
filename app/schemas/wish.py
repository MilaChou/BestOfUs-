from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.enums import Budget, GiftType, WishPriority, budget_for_price

Price = Field(default=None, ge=0, le=100_000_000, description="Rubles. 0 = своими руками.")


class WishCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    link: str | None = Field(default=None, max_length=500)
    price: int | None = Price
    image_url: str | None = Field(default=None, max_length=500)
    note: str | None = Field(default=None, max_length=2000)
    priority: WishPriority = WishPriority.NICE
    gift_type: GiftType | None = None


class WishUpdate(BaseModel):
    """Only the fields that are sent get changed."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(default=None, min_length=1, max_length=200)
    link: str | None = Field(default=None, max_length=500)
    price: int | None = Price
    image_url: str | None = Field(default=None, max_length=500)
    note: str | None = Field(default=None, max_length=2000)
    priority: WishPriority = None
    gift_type: GiftType | None = None


class MyWishRead(BaseModel):
    """How the owner sees their own wish: no word about reservations."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    link: str | None
    price: int | None
    image_url: str | None
    note: str | None
    priority: WishPriority
    gift_type: GiftType | None
    is_received: bool
    received_at: datetime | None
    created_at: datetime

    @computed_field
    @property
    def budget(self) -> Budget | None:
        return budget_for_price(self.price)


class PartnerWishRead(MyWishRead):
    """How the partner sees it: plus whether it's already reserved (by them)."""

    is_reserved: bool


class GiftNoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    note: str | None = Field(default=None, max_length=2000)
    link: str | None = Field(default=None, max_length=500)
    price: int | None = Price
    gift_type: GiftType | None = None


class GiftNoteUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(default=None, min_length=1, max_length=200)
    note: str | None = Field(default=None, max_length=2000)
    link: str | None = Field(default=None, max_length=500)
    price: int | None = Price
    gift_type: GiftType | None = None
    is_gifted: bool = None


class GiftNoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    note: str | None
    link: str | None
    price: int | None
    gift_type: GiftType | None
    catalog_id: str | None
    is_gifted: bool
    created_at: datetime

    @computed_field
    @property
    def budget(self) -> Budget | None:
        return budget_for_price(self.price)


class CatalogGiftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    gift_type: GiftType
    budget: Budget
    personalized: bool
    hint: str | None


class GiftSuggestion(BaseModel):
    """Result of "Что подарить?" — exactly one of wish / note / gift is filled."""

    source: Literal["wishlist", "note", "catalog"]
    wish: PartnerWishRead | None = None
    note: GiftNoteRead | None = None
    gift: CatalogGiftRead | None = None
    warning: str | None = Field(default=None, description="Reminder about the partner's allergies.")
