# BESTOFUS

A shared digital space for couples to organize their everyday life.

## Development

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync                      # install dependencies
cp .env.example .env         # local settings
uv run alembic upgrade head  # create / update the database tables
uv run fastapi dev           # dev server at http://127.0.0.1:8000 (docs at /docs)
uv run pytest                # tests
uv run ruff check . && uv run ruff format .
```

### Database migrations

Models live in `app/models/`. After changing a model:

```bash
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic upgrade head
```
