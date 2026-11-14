import random
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import CurrentUser
from app.database import DbSession
from app.enums import Budget, GiftType, budget_for_price
from app.gift_catalog import GIFTS, CatalogGift, personalized_gifts
from app.models import GiftNote, Wish
from app.schemas.wish import CatalogGiftRead, GiftNoteRead, GiftSuggestion, PartnerWishRead

router = APIRouter(prefix="/gifts", tags=["gifts"])


def fits(
    gift_type: GiftType | None,
    item_budget: Budget | None,
    want_type: GiftType | None,
    want_budget: Budget | None,
) -> bool:
    # A wish without a type can't be said to be "для дома", so it doesn't match a type filter.
    if want_type is not None and gift_type != want_type:
        return False
    # A wish without a price might be any price, so it isn't hidden by a budget filter.
    if want_budget is not None and item_budget is not None and item_budget != want_budget:
        return False
    return True


@router.get("/catalog", response_model=list[CatalogGiftRead])
def gift_catalog(
    gift_type: GiftType | None = None, budget: Budget | None = None
) -> list[CatalogGift]:
    """The built-in gift catalog (without personal gifts). Open to everyone."""
    return [g for g in GIFTS if fits(g.gift_type, g.budget, gift_type, budget)]


@router.get("/suggest", response_model=GiftSuggestion)
def suggest_gift(
    user: CurrentUser,
    db: DbSession,
    budget: Budget | None = None,
    gift_type: GiftType | None = None,
    exclude_wishes: Annotated[list[int] | None, Query()] = None,
    exclude_notes: Annotated[list[int] | None, Query()] = None,
    exclude_catalog: Annotated[list[str] | None, Query()] = None,
) -> GiftSuggestion:
    """«Что подарить?» — one gift idea for the partner.

    Looks in this order: 1) the partner's wishlist (not received, not reserved),
    2) your secret notes, 3) gifts made from the partner's profile,
    4) the general catalog. For "ещё", send what you've seen in the exclude_* lists.
    """
    skip_wishes, skip_notes = set(exclude_wishes or []), set(exclude_notes or [])
    skip_catalog = set(exclude_catalog or [])
    partner = user.partner

    # 1. What the partner wished for themself.
    if partner is not None:
        wishes = db.scalars(
            select(Wish).where(
                Wish.owner_id == partner.id,
                Wish.is_received.is_(False),
                Wish.reserved_by_id.is_(None),
            )
        )
        matching = [
            w
            for w in wishes
            if w.id not in skip_wishes
            and fits(w.gift_type, budget_for_price(w.price), gift_type, budget)
        ]
        if matching:
            wish = PartnerWishRead.model_validate(random.choice(matching))
            return GiftSuggestion(source="wishlist", wish=wish)

    # 2. Your own secret notes.
    notes = list(db.scalars(select(GiftNote).where(GiftNote.author_id == user.id)))
    matching_notes = [
        n
        for n in notes
        if not n.is_gifted
        and n.id not in skip_notes
        and fits(n.gift_type, budget_for_price(n.price), gift_type, budget)
    ]
    if matching_notes:
        note = GiftNoteRead.model_validate(random.choice(matching_notes))
        return GiftSuggestion(source="note", note=note)

    # 3–4. Personal gifts from the profile first, then the general catalog.
    profile = partner.profile if partner is not None else None
    saved = {n.catalog_id for n in notes if n.catalog_id}
    for pool in (personalized_gifts(profile), GIFTS):
        candidates = [
            g
            for g in pool
            if g.id not in skip_catalog
            and g.id not in saved
            and fits(g.gift_type, g.budget, gift_type, budget)
        ]
        if candidates:
            gift = random.choice(candidates)
            warning = None
            if gift.allergy_sensitive and profile is not None and profile.allergies:
                warning = f"Проверь аллергии партнёра: {profile.allergies}"
            return GiftSuggestion(
                source="catalog", gift=CatalogGiftRead.model_validate(gift), warning=warning
            )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Nothing matches these filters — try fewer of them",
    )
