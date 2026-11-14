import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app import push
from app.models import Device, User
from app.push import send_messages as real_send_messages  # imported before the autouse fake


def test_sends_in_batches_and_drops_dead_tokens(
    db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    user = User(email="a@example.com", hashed_password="x")
    db_session.add(user)
    db_session.flush()
    for token in ("ExponentPushToken[alive]", "ExponentPushToken[dead]"):
        db_session.add(Device(user_id=user.id, push_token=token, platform="ios"))
    db_session.commit()

    calls: list[list[dict]] = []

    def fake_post(url: str, json: list[dict], headers: dict, timeout: int) -> httpx.Response:
        calls.append(json)
        tickets = [
            {"status": "error", "details": {"error": "DeviceNotRegistered"}}
            if m["to"].endswith("[dead]")
            else {"status": "ok", "id": "x"}
            for m in json
        ]
        return httpx.Response(200, json={"data": tickets}, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(push, "SessionLocal", sessionmaker(bind=db_session.get_bind()))

    messages = [{"to": "ExponentPushToken[alive]", "title": "t", "body": "b"}] * 150
    messages.append({"to": "ExponentPushToken[dead]", "title": "t", "body": "b"})
    real_send_messages(messages)

    assert [len(batch) for batch in calls] == [100, 51]
    db_session.expire_all()
    assert list(db_session.scalars(select(Device.push_token))) == ["ExponentPushToken[alive]"]


def test_network_errors_never_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken_post(*args: object, **kwargs: object) -> httpx.Response:
        raise httpx.ConnectError("no internet")

    monkeypatch.setattr(httpx, "post", broken_post)
    real_send_messages([{"to": "ExponentPushToken[x]", "title": "t", "body": "b"}])  # no exception
