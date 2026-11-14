from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.database import DbSession
from app.models import Couple, User
from app.security import decode_access_token

# Tells FastAPI (and the "Authorize" button in /docs) where to get a token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_prefix}/auth/login")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> User:
    user_id = decode_access_token(token)
    user = db.get(User, user_id) if user_id is not None else None
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_couple(user: CurrentUser) -> Couple:
    if user.couple is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not in a couple yet",
        )
    return user.couple


CurrentCouple = Annotated[Couple, Depends(get_current_couple)]
