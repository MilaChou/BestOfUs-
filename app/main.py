from fastapi import FastAPI

from app.api import (
    auth,
    catalog,
    couple,
    gift_notes,
    gifts,
    health,
    ideas,
    love_language,
    memories,
    notifications,
    tasks,
    users,
    wishlist,
)
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    description="A shared digital space for couples to organize their everyday life.",
    version="0.1.0",
    debug=settings.debug,
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(users.router, prefix=settings.api_prefix)
app.include_router(couple.router, prefix=settings.api_prefix)
app.include_router(ideas.router, prefix=settings.api_prefix)
app.include_router(catalog.router, prefix=settings.api_prefix)
app.include_router(wishlist.router, prefix=settings.api_prefix)
app.include_router(gift_notes.router, prefix=settings.api_prefix)
app.include_router(gifts.router, prefix=settings.api_prefix)
app.include_router(tasks.router, prefix=settings.api_prefix)
app.include_router(memories.router, prefix=settings.api_prefix)
app.include_router(love_language.router, prefix=settings.api_prefix)
app.include_router(notifications.router, prefix=settings.api_prefix)
