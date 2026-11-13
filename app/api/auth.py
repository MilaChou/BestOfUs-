from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.database import DbSession
from app.models import Profile, User
from app.schemas.user import UserCreate, UserRead
from app.security import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: DbSession) -> User:
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    user = User(
        email=email,
        hashed_password=hash_password(data.password),
        profile=Profile(name=data.name),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
