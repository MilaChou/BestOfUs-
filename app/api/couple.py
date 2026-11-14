from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_, select, update

from app.api.deps import CurrentCouple, CurrentUser
from app.database import DbSession
from app.media import delete_photo_file
from app.models import Couple, Wish
from app.models.couple import generate_invite_code
from app.schemas.couple import CoupleCreate, CoupleJoin, CoupleRead, CoupleUpdate

router = APIRouter(prefix="/couple", tags=["couple"])


def new_unique_invite_code(db: DbSession) -> str:
    while True:
        code = generate_invite_code()
        if db.scalar(select(Couple.id).where(Couple.invite_code == code)) is None:
            return code


@router.post("", response_model=CoupleRead, status_code=status.HTTP_201_CREATED)
def create_couple(data: CoupleCreate, user: CurrentUser, db: DbSession) -> Couple:
    """Create a shared space and get an invite code for the partner."""
    if user.couple is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="You are already in a couple"
        )

    couple = Couple(**data.model_dump(), invite_code=new_unique_invite_code(db))
    couple.members.append(user)
    db.add(couple)
    db.commit()
    db.refresh(couple)
    return couple


@router.post("/join", response_model=CoupleRead)
def join_couple(data: CoupleJoin, user: CurrentUser, db: DbSession) -> Couple:
    """Join the partner's couple with their invite code."""
    if user.couple is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="You are already in a couple"
        )

    code = data.invite_code.strip().upper()
    couple = db.scalar(select(Couple).where(Couple.invite_code == code))
    if couple is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid invite code")
    if couple.is_full:  # normally can't happen: the code is cleared when the couple fills up
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This couple is full")

    couple.members.append(user)
    if couple.is_full:
        couple.invite_code = None
    db.commit()
    db.refresh(couple)
    return couple


@router.get("", response_model=CoupleRead)
def read_couple(couple: CurrentCouple) -> Couple:
    """My couple, with both members' profiles."""
    return couple


@router.patch("", response_model=CoupleRead)
def update_couple(data: CoupleUpdate, couple: CurrentCouple, db: DbSession) -> Couple:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(couple, field, value)
    db.commit()
    db.refresh(couple)
    return couple


@router.post("/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_couple(user: CurrentUser, couple: CurrentCouple, db: DbSession) -> None:
    """Leave the couple. The last one to leave deletes it."""
    # Reservations ("Я подарю") between the two make no sense any more.
    db.execute(
        update(Wish)
        .where(or_(Wish.owner_id == user.id, Wish.reserved_by_id == user.id))
        .where(Wish.reserved_by_id.is_not(None))
        .values(reserved_by_id=None, reserved_at=None)
    )
    couple.members.remove(user)
    files_to_delete: list[str] = []
    if not couple.members:
        files_to_delete = [p.filename for m in couple.memories for p in m.photos]
        db.delete(couple)
    else:
        # The one who stays can invite someone again.
        couple.invite_code = new_unique_invite_code(db)
    db.commit()
    # Only after the database change is saved, so a failed save loses no photos.
    for filename in files_to_delete:
        delete_photo_file(filename)
