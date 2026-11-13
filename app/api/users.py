from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.database import DbSession
from app.models import Profile, User
from app.schemas.user import ProfileUpdate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_me(user: CurrentUser) -> User:
    return user


@router.patch("/me/profile", response_model=UserRead)
def update_my_profile(data: ProfileUpdate, user: CurrentUser, db: DbSession) -> User:
    """Change only the fields that were sent; send null to clear a field."""
    profile: Profile = user.profile
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(user)
    return user
