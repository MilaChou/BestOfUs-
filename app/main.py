from fastapi import FastAPI

from app.api import auth, health, users
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
