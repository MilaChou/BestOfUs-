from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# SQLite allows a connection to be used only by the thread that created it;
# FastAPI runs sync endpoints in a thread pool, so that check has to be off.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Parent class for all database models (tables)."""


def get_db() -> Iterator[Session]:
    """Give one endpoint call its own session and always close it afterwards."""
    with SessionLocal() as session:
        yield session


DbSession = Annotated[Session, Depends(get_db)]
