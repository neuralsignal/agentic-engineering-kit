---
name: fastapi-minimal
description: Scaffold a minimal async FastAPI + SQLModel project (SQLite, no Docker needed). CRUD API with Alembic migrations, pydantic-settings config, and pytest-asyncio tests.
---

# FastAPI Minimal Skill

**Trigger:** Use when asked to scaffold a lightweight Python API service — quick prototype, internal tool, data pipeline endpoint, or anything that doesn't need PostgreSQL, auth, or a separate frontend.

**When to use minimal vs fullstack:**
- **Minimal** → single-service API, SQLite (swap URL to upgrade to Postgres), lightweight dev loop, no Docker required
- **Fullstack** → multi-user app, JWT auth, PostgreSQL, Docker Compose, React frontend

See `skills/fastapi-fullstack/SKILL.md` for the production full-stack alternative.

## Locations

- `skills/fastapi-minimal/scripts/init_fastapi.py` — project generator

## Running Scripts

```bash
python skills/fastapi-minimal/scripts/init_fastapi.py <project-name>
```

With pixi:
```bash
cd skills/fastapi-minimal && pixi run python scripts/init_fastapi.py <project-name>
```

With uv:
```bash
cd skills/fastapi-minimal && uv run python scripts/init_fastapi.py <project-name>
```

The generated project is created at `<CWD>/<project-name>/`.

## Generated Project Structure

```
<project-name>/
├── pyproject.toml                    # all deps: FastAPI, SQLModel, pytest, ruff, etc.
├── .env                              # DATABASE_URL, SECRET_KEY, APP_NAME
├── alembic.ini
├── alembic/
│   ├── env.py                        # async-compatible, runs against SQLModel metadata
│   └── versions/
├── src/
│   └── <package_name>/
│       ├── __init__.py
│       ├── main.py                   # FastAPI app + lifespan + routers
│       ├── db.py                     # async engine + get_session dependency
│       ├── settings.py               # pydantic-settings (reads from .env, no defaults)
│       ├── models.py                 # SQLModel table definitions
│       ├── schemas.py                # Pydantic v2 request/response schemas
│       └── routers/
│           ├── __init__.py
│           ├── health.py             # GET /health → {"status":"ok","db":"ok"}
│           └── items.py              # CRUD: POST/GET/GET{id}/PATCH/DELETE /items
└── tests/
    ├── conftest.py                   # in-memory SQLite + async httpx TestClient fixture
    └── test_health.py                # 1 test: health endpoint
```

## Tech Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| API framework | FastAPI + Uvicorn | Async HTTP, OpenAPI auto-docs |
| ORM + validation | SQLModel | SQLAlchemy + Pydantic v2 in one |
| Database | SQLite via aiosqlite | No Docker; swap URL for Postgres |
| Migrations | Alembic | Schema versioning |
| Config | pydantic-settings | All config from `.env`, no code defaults |
| Tests | pytest + pytest-asyncio + httpx | Async test client, in-memory DB |
| Property tests | hypothesis | Available for pure function testing |
| Linting | ruff | Formatting + lint in one tool |

## Workflow After Scaffolding

```bash
cd <project-name>

# Install deps (choose your package manager)
pip install -e ".[dev]"    # pip + venv
# or: uv sync
# or: pixi install

# Run dev server
uvicorn src.<package_name>.main:app --reload

# Run tests
pytest

# Lint
ruff check src/
ruff format src/

# Create and apply a migration after editing models.py
alembic revision --autogenerate -m "add items table"
alembic upgrade head
```

## Adding a New Router

1. Create `src/<package_name>/routers/<name>.py` with `router = APIRouter(...)`
2. Add the router in `main.py`: `app.include_router(<name>.router)`
3. Add model class to `models.py` (SQLModel table)
4. Add schema classes to `schemas.py` (request/response)
5. Run `alembic revision --autogenerate -m "<description>"` to generate migration
6. Write tests in `tests/test_<name>.py` using the `client` fixture

## Upgrading to PostgreSQL

1. Install the async Postgres driver: add `asyncpg>=0.30,<0.31` to your deps
2. Update `.env`: `DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname`
3. Update `alembic.ini`: `sqlalchemy.url = postgresql://user:password@localhost/dbname`
4. Run `alembic upgrade head` to apply migrations to the new DB

## Engineering Principles Applied to Generated Code

- **Everything from config** — `pydantic-settings` reads all values from `.env`; missing var = startup crash with clear error. No defaults in code.
- **Descriptive package name** — generated package uses `<project_name>` (not `src` or `app`)
- **Fail fast** — no silent exception handling; FastAPI 422 validation errors propagate automatically
- **TDD-ready** — `conftest.py` sets up in-memory DB; first test included; `hypothesis` in deps
- **Modular** — each router is independent; add/remove routers without touching others
