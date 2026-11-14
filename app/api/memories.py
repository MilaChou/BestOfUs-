from datetime import date
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select

from app.api.deps import CurrentCouple, CurrentUser
from app.database import DbSession
from app.enums import NotificationType
from app.media import delete_photo_file, photo_path, save_photo
from app.models import Couple, Idea, Memory, MemoryPhoto, User
from app.notifications import notify_partner
from app.schemas.memory import MemoryCreate, MemoryRead, MemoryUpdate

router = APIRouter(prefix="/couple/memories", tags=["memories"])

MAX_PHOTOS = 10


def notify_memory_added(
    db: DbSession, background: BackgroundTasks, user: User, memory: Memory
) -> None:
    notify_partner(
        db,
        background,
        user,
        NotificationType.MEMORY_ADDED,
        "📸 Новое воспоминание",
        f"«{memory.title}»",
        {"memory_id": memory.id},
    )


def get_couple_memory(memory_id: int, couple: Couple, db: DbSession) -> Memory:
    memory = db.get(Memory, memory_id)
    if memory is None or memory.couple_id != couple.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory not found")
    return memory


@router.get("", response_model=list[MemoryRead])
def list_memories(couple: CurrentCouple, db: DbSession, year: int | None = None) -> list[Memory]:
    """All memories, the most recent first. Optional filter by year."""
    memories = db.scalars(
        select(Memory)
        .where(Memory.couple_id == couple.id)
        .order_by(Memory.happened_on.desc(), Memory.id.desc())
    )
    return [m for m in memories if year is None or m.happened_on.year == year]


@router.get("/on-this-day", response_model=list[MemoryRead])
def on_this_day(couple: CurrentCouple, db: DbSession) -> list[Memory]:
    """«В этот день»: memories from today's date in earlier years."""
    today = date.today()
    memories = db.scalars(
        select(Memory).where(Memory.couple_id == couple.id).order_by(Memory.happened_on.desc())
    )
    return [
        m
        for m in memories
        if (m.happened_on.month, m.happened_on.day) == (today.month, today.day)
        and m.happened_on.year < today.year
    ]


@router.post("", response_model=MemoryRead, status_code=status.HTTP_201_CREATED)
def create_memory(
    data: MemoryCreate,
    user: CurrentUser,
    couple: CurrentCouple,
    db: DbSession,
    background: BackgroundTasks,
) -> Memory:
    """Create a memory. Add photos to it afterwards with POST /{id}/photos."""
    memory = Memory(**data.model_dump(), couple=couple, author_id=user.id)
    db.add(memory)
    db.flush()
    notify_memory_added(db, background, user, memory)
    db.commit()
    db.refresh(memory)
    return memory


@router.post("/from-idea/{idea_id}", response_model=MemoryRead, status_code=status.HTTP_201_CREATED)
def create_from_idea(
    idea_id: int,
    user: CurrentUser,
    couple: CurrentCouple,
    db: DbSession,
    background: BackgroundTasks,
) -> Memory:
    """Turn a done idea into a memory: its title, review and the day it was done."""
    idea = db.get(Idea, idea_id)
    if idea is None or idea.couple_id != couple.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    if not idea.is_done or idea.done_at is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Mark the idea as done first"
        )
    if db.scalar(select(Memory.id).where(Memory.idea_id == idea.id)) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="This idea already has a memory"
        )

    memory = Memory(
        couple=couple,
        author_id=user.id,
        idea_id=idea.id,
        title=idea.title,
        description=idea.review or idea.description,
        happened_on=idea.done_at.date(),
    )
    db.add(memory)
    db.flush()
    notify_memory_added(db, background, user, memory)
    db.commit()
    db.refresh(memory)
    return memory


@router.get("/{memory_id}", response_model=MemoryRead)
def read_memory(memory_id: int, couple: CurrentCouple, db: DbSession) -> Memory:
    return get_couple_memory(memory_id, couple, db)


@router.patch("/{memory_id}", response_model=MemoryRead)
def update_memory(
    memory_id: int, data: MemoryUpdate, couple: CurrentCouple, db: DbSession
) -> Memory:
    memory = get_couple_memory(memory_id, couple, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(memory, field, value)
    db.commit()
    db.refresh(memory)
    return memory


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(memory_id: int, couple: CurrentCouple, db: DbSession) -> None:
    memory = get_couple_memory(memory_id, couple, db)
    filenames = [p.filename for p in memory.photos]
    db.delete(memory)
    db.commit()
    for filename in filenames:  # after the commit, so a failed save loses no photos
        delete_photo_file(filename)


# --- Photos ----------------------------------------------------------------


@router.post("/{memory_id}/photos", response_model=MemoryRead)
def upload_photos(
    memory_id: int,
    files: Annotated[list[UploadFile], File(description="Up to 10 photos per memory, 10 MB each")],
    user: CurrentUser,
    couple: CurrentCouple,
    db: DbSession,
    background: BackgroundTasks,
) -> Memory:
    memory = get_couple_memory(memory_id, couple, db)
    if len(memory.photos) + len(files) > MAX_PHOTOS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A memory can have at most {MAX_PHOTOS} photos",
        )

    saved: list[str] = []
    try:
        for upload in files:
            filename, content_type = save_photo(upload)
            saved.append(filename)
            memory.photos.append(MemoryPhoto(filename=filename, content_type=content_type))
        notify_partner(
            db,
            background,
            user,
            NotificationType.PHOTOS_ADDED,
            "📸 Новые фото",
            f"{len(files)} фото в «{memory.title}»",
            {"memory_id": memory.id},
        )
        db.commit()
    except Exception:
        # One bad file -> nothing is kept, so there are no half-uploaded memories.
        db.rollback()
        for filename in saved:
            delete_photo_file(filename)
        raise
    db.refresh(memory)
    return memory


def get_photo(memory_id: int, photo_id: int, couple: Couple, db: DbSession) -> MemoryPhoto:
    memory = get_couple_memory(memory_id, couple, db)
    photo = next((p for p in memory.photos if p.id == photo_id), None)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo


@router.get("/{memory_id}/photos/{photo_id}", response_class=FileResponse)
def download_photo(
    memory_id: int, photo_id: int, couple: CurrentCouple, db: DbSession
) -> FileResponse:
    """The photo itself — only for members of the couple."""
    photo = get_photo(memory_id, photo_id, couple, db)
    path = photo_path(photo.filename)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo file is missing")
    return FileResponse(path, media_type=photo.content_type)


@router.delete("/{memory_id}/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(memory_id: int, photo_id: int, couple: CurrentCouple, db: DbSession) -> None:
    photo = get_photo(memory_id, photo_id, couple, db)
    filename = photo.filename
    db.delete(photo)
    db.commit()
    delete_photo_file(filename)
