# BESTOFUS

A shared digital space for couples to organize their everyday life.

## Development

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync                      # install dependencies
cp .env.example .env         # local settings, then fill in SECRET_KEY (see the comment there)
uv run alembic upgrade head  # create / update the database tables
uv run fastapi dev           # dev server at http://127.0.0.1:8000 (docs at /docs)
uv run pytest                # tests
uv run ruff check . && uv run ruff format .
```

### Using the API from a phone on the same Wi-Fi

`uv run fastapi dev` listens only on this computer. To reach it from a phone
(or the Expo app) on the same Wi-Fi, listen on all network interfaces:

```bash
uv run fastapi dev --host 0.0.0.0
```

Then use `http://<this Mac's Wi-Fi IP>:8000` on the phone
(find the IP with `ipconfig getifaddr en0`). In the Android emulator use `http://10.0.2.2:8000`.

### Database migrations

Models live in `app/models/`. After changing a model:

```bash
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic upgrade head
```

### Daily reminders

Birthdays, anniversaries, tasks for today and "on this day" memories are created by
a job that should run once a day on the server (running it twice is safe):

```bash
uv run python -m app.reminders
```
