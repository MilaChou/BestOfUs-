from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser
from app.database import DbSession
from app.gift_catalog import GIFTS, personalized_gifts
from app.models import GiftNote, User
from app.schemas.wish import GiftNoteCreate, GiftNoteRead, GiftNoteUpdate

router = APIRouter(prefix="/gift-notes", tags=["gift notes"])


def get_note(note_id: int, user: User, db: DbSession) -> GiftNote:
    note = db.get(GiftNote, note_id)
    if note is None or note.author_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


@router.get("", response_model=list[GiftNoteRead])
def list_notes(user: CurrentUser, db: DbSession, is_gifted: bool | None = None) -> list[GiftNote]:
    """🤫 Your secret "what to gift" notes. Nobody else can see them."""
    stmt = select(GiftNote).where(GiftNote.author_id == user.id)
    if is_gifted is not None:
        stmt = stmt.where(GiftNote.is_gifted == is_gifted)
    stmt = stmt.order_by(GiftNote.is_gifted, GiftNote.created_at.desc(), GiftNote.id.desc())
    return list(db.scalars(stmt))


@router.post("", response_model=GiftNoteRead, status_code=status.HTTP_201_CREATED)
def add_note(data: GiftNoteCreate, user: CurrentUser, db: DbSession) -> GiftNote:
    note = GiftNote(**data.model_dump(), author_id=user.id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.post(
    "/from-catalog/{catalog_id}", response_model=GiftNoteRead, status_code=status.HTTP_201_CREATED
)
def save_from_catalog(catalog_id: str, user: CurrentUser, db: DbSession) -> GiftNote:
    """Liked a gift from "Что подарить?" — keep it in your secret notes."""
    partner_profile = user.partner.profile if user.partner else None
    gift = next(
        (g for g in personalized_gifts(partner_profile) + GIFTS if g.id == catalog_id), None
    )
    if gift is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such gift")
    exists = db.scalar(
        select(GiftNote.id).where(GiftNote.author_id == user.id, GiftNote.catalog_id == catalog_id)
    )
    if exists is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already in your notes")

    note = GiftNote(
        author_id=user.id,
        catalog_id=gift.id,
        title=gift.title,
        note=gift.description,
        gift_type=gift.gift_type,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.patch("/{note_id}", response_model=GiftNoteRead)
def update_note(note_id: int, data: GiftNoteUpdate, user: CurrentUser, db: DbSession) -> GiftNote:
    note = get_note(note_id, user, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, user: CurrentUser, db: DbSession) -> None:
    db.delete(get_note(note_id, user, db))
    db.commit()
