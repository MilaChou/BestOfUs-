"""Sending push notifications through Expo's push service.

The phone app (made with Expo) registers and gets a push token; the backend
sends messages for that token to Expo, and Expo delivers them via Apple (iOS)
or Google (Android). If Expo says a token is dead (the app was deleted),
the token is removed so we stop sending to it.
"""

import logging

import httpx
from sqlalchemy import delete

from app.config import settings
from app.database import SessionLocal

log = logging.getLogger(__name__)

BATCH_SIZE = 100  # Expo accepts up to 100 messages per request


def send_messages(messages: list[dict]) -> None:
    """Deliver messages like {"to": token, "title": ..., "body": ..., "data": {...}}.

    Never raises: a failed push must not break anything else.
    """
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if settings.expo_access_token:
        headers["Authorization"] = f"Bearer {settings.expo_access_token}"

    dead_tokens: list[str] = []
    for start in range(0, len(messages), BATCH_SIZE):
        batch = messages[start : start + BATCH_SIZE]
        try:
            response = httpx.post(settings.expo_push_url, json=batch, headers=headers, timeout=10)
            response.raise_for_status()
            tickets = response.json().get("data", [])
        except (httpx.HTTPError, ValueError):
            log.exception("Push sending failed")
            continue
        for message, ticket in zip(batch, tickets, strict=False):
            if ticket.get("details", {}).get("error") == "DeviceNotRegistered":
                dead_tokens.append(message["to"])

    if dead_tokens:
        from app.models import Device

        with SessionLocal() as db:
            db.execute(delete(Device).where(Device.push_token.in_(dead_tokens)))
            db.commit()
