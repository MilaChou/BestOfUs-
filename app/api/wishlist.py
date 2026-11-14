from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser
from app.database import DbSession
from app.enums import NotificationType, WishPriority
from app.models import User, Wish
from app.notifications import notify_partner
from app.schemas.wish import MyWishRead, PartnerWishRead, WishCreate, WishUpdate

router = APIRouter(prefix="/wishlist", tags=["wishlist"])

PRIORITY_ORDER = list(WishPriority)


def sorted_wishes(wishes: list[Wish]) -> list[Wish]:
    """Not received first, then 🔥 → 🙂 → ✨, then newest."""
    by_newest = sorted(wishes, key=lambda w: (w.created_at, w.id), reverse=True)
    return sorted(by_newest, key=lambda w: (w.is_received, PRIORITY_ORDER.index(w.priority)))


def wishes_of(owner: User, db: DbSession, is_received: bool | None) -> list[Wish]:
    stmt = select(Wish).where(Wish.owner_id == owner.id)
    if is_received is not None:
        stmt = stmt.where(Wish.is_received == is_received)
    return sorted_wishes(list(db.scalars(stmt)))


def get_partner(user: User) -> User:
    if user.partner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You have no partner yet")
    return user.partner


def get_wish(wish_id: int, owner: User, db: DbSession) -> Wish:
    wish = db.get(Wish, wish_id)
    if wish is None or wish.owner_id != owner.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wish not found")
    return wish


# --- My own wishlist -------------------------------------------------------


@router.get("/me", response_model=list[MyWishRead])
def my_wishlist(user: CurrentUser, db: DbSession, is_received: bool | None = None) -> list[Wish]:
    return wishes_of(user, db, is_received)


@router.post("/me", response_model=MyWishRead, status_code=status.HTTP_201_CREATED)
def add_wish(
    data: WishCreate, user: CurrentUser, db: DbSession, background: BackgroundTasks
) -> Wish:
    wish = Wish(**data.model_dump(), owner_id=user.id)
    db.add(wish)
    db.flush()
    notify_partner(
        db,
        background,
        user,
        NotificationType.WISH_ADDED,
        "🎁 Новое желание в вишлисте",
        f"«{wish.title}»",
        {"wish_id": wish.id},
    )
    db.commit()
    db.refresh(wish)
    return wish


@router.patch("/me/{wish_id}", response_model=MyWishRead)
def update_wish(wish_id: int, data: WishUpdate, user: CurrentUser, db: DbSession) -> Wish:
    wish = get_wish(wish_id, user, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(wish, field, value)
    db.commit()
    db.refresh(wish)
    return wish


@router.delete("/me/{wish_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wish(wish_id: int, user: CurrentUser, db: DbSession) -> None:
    db.delete(get_wish(wish_id, user, db))
    db.commit()


@router.post("/me/{wish_id}/received", response_model=MyWishRead)
def mark_received(wish_id: int, user: CurrentUser, db: DbSession) -> Wish:
    """«Мне это подарили» 🎉"""
    wish = get_wish(wish_id, user, db)
    wish.is_received = True
    wish.received_at = datetime.now(UTC)
    db.commit()
    db.refresh(wish)
    return wish


@router.delete("/me/{wish_id}/received", response_model=MyWishRead)
def unmark_received(wish_id: int, user: CurrentUser, db: DbSession) -> Wish:
    wish = get_wish(wish_id, user, db)
    wish.is_received = False
    wish.received_at = None
    db.commit()
    db.refresh(wish)
    return wish


# --- Partner's wishlist ----------------------------------------------------


@router.get("/partner", response_model=list[PartnerWishRead])
def partner_wishlist(
    user: CurrentUser, db: DbSession, is_received: bool | None = None
) -> list[Wish]:
    """The partner's wishes, with `is_reserved` — which the partner themself never sees."""
    return wishes_of(get_partner(user), db, is_received)


@router.post("/partner/{wish_id}/reserve", response_model=PartnerWishRead)
def reserve(wish_id: int, user: CurrentUser, db: DbSession) -> Wish:
    """«Я подарю» 🎁 — a secret: the owner won't see it."""
    wish = get_wish(wish_id, get_partner(user), db)
    if wish.is_received:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already received")
    if wish.reserved_by_id is None:
        wish.reserved_by_id = user.id
        wish.reserved_at = datetime.now(UTC)
        db.commit()
        db.refresh(wish)
    return wish


@router.delete("/partner/{wish_id}/reserve", response_model=PartnerWishRead)
def cancel_reservation(wish_id: int, user: CurrentUser, db: DbSession) -> Wish:
    wish = get_wish(wish_id, get_partner(user), db)
    if wish.reserved_by_id == user.id:
        wish.reserved_by_id = None
        wish.reserved_at = None
        db.commit()
        db.refresh(wish)
    return wish
