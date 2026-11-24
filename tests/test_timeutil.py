import time
from datetime import UTC, date, datetime

import pytest

from app.timeutil import local_date


@pytest.fixture
def moscow_clock(monkeypatch: pytest.MonkeyPatch):
    """Pretend the server's clock is in Moscow (UTC+3)."""
    monkeypatch.setenv("TZ", "Europe/Moscow")
    time.tzset()
    yield
    monkeypatch.undo()
    time.tzset()


def test_after_midnight_in_moscow_is_the_next_day(moscow_clock: None) -> None:
    late_evening_utc = datetime(2026, 11, 14, 21, 30)  # 00:30 on the 15th in Moscow
    assert local_date(late_evening_utc) == date(2026, 11, 15)  # naive = UTC, as SQLite returns it
    assert local_date(late_evening_utc.replace(tzinfo=UTC)) == date(2026, 11, 15)


def test_daytime_stays_the_same_day(moscow_clock: None) -> None:
    assert local_date(datetime(2026, 11, 14, 9, 0)) == date(2026, 11, 14)
