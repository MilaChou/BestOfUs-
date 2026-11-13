# BESTOFUS

A shared digital space for couples to organize their everyday life.

## Development

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync                      # install dependencies
cp .env.example .env         # local settings
uv run fastapi dev           # dev server at http://127.0.0.1:8000 (docs at /docs)
uv run pytest                # tests
uv run ruff check . && uv run ruff format .
```
