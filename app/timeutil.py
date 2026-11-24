"""Turning stored moments into calendar days people expect."""

from datetime import UTC, date, datetime


def local_date(moment: datetime) -> date:
    """The day on the server's clock when this moment happened.

    Moments are saved in UTC. SQLite returns them without a time zone, so a
    "naive" value is treated as UTC. Without this, something done at 00:30 in
    Moscow (21:30 UTC) would land on the previous day.
    """
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    return moment.astimezone().date()
