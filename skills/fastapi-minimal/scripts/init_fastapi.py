#!/usr/bin/env python3
"""init_fastapi.py — scaffold a minimal async FastAPI + SQLModel project.

Usage:
    pixi run python scripts/init_fastapi.py <project-name>

Generates a complete project tree at <project-name>/ relative to CWD.
"""

import sys
import textwrap
from pathlib import Path


# ── Argument validation ──────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: pixi run python scripts/init_fastapi.py <project-name>")
        print("Example: pixi run python scripts/init_fastapi.py my-api")
        sys.exit(1)

    project_name = sys.argv[1]

    # Validate: must be valid identifier when hyphens replaced with underscores
    package_name = project_name.replace("-", "_")
    if not package_name.isidentifier():
        print(f"❌ '{project_name}' is not a valid project name.")
        print("   Use lowercase letters, numbers, and hyphens only.")
        sys.exit(1)

    target = Path.cwd() / project_name
    if target.exists():
        print(f"❌ Directory '{project_name}' already exists.")
        sys.exit(1)

    scaffold(project_name, package_name, target)
    print(f"\n✅ Project '{project_name}' created at {target}")
    print("\nNext steps:")
    print(f"  cd {project_name}")
    print("  pixi install")
    print("  pixi run uvicorn src." + package_name + ".main:app --reload")
    print("  # or run tests:")
    print("  pixi run pytest")


# ── File content generators ──────────────────────────────────────────────────

def scaffold(project_name: str, package_name: str, target: Path) -> None:
    print(f"🚀 Scaffolding '{project_name}'...")

    files: dict[str, str] = {}

    files["pixi.toml"] = textwrap.dedent(f"""\
        [workspace]
        channels = ["conda-forge"]
        name = "{project_name}"
        platforms = ["linux-64"]
        version = "0.1.0"

        [dependencies]
        python = ">=3.12,<3.15"

        [pypi-dependencies]
        fastapi = ">=0.115,<0.116"
        uvicorn = {{version = ">=0.32,<0.33", extras = ["standard"]}}
        sqlmodel = ">=0.0.22,<0.1"
        pydantic-settings = ">=2.6,<3"
        aiosqlite = ">=0.20,<0.21"
        alembic = ">=1.14,<2"
        pytest = ">=8.3,<9"
        pytest-asyncio = ">=0.24,<1"
        httpx = ">=0.28,<0.29"
        hypothesis = ">=6.122,<7"
        ruff = ">=0.8,<1"
        {package_name} = {{path = ".", editable = true}}
    """)

    files["pyproject.toml"] = textwrap.dedent(f"""\
        [build-system]
        requires = ["hatchling"]
        build-backend = "hatchling.build"

        [project]
        name = "{project_name}"
        version = "0.1.0"
        requires-python = ">=3.12"

        [tool.hatch.build.targets.wheel]
        packages = ["src/{package_name}"]

        [tool.pytest.ini_options]
        asyncio_mode = "auto"
        testpaths = ["tests"]

        [tool.ruff.lint]
        select = ["E", "F", "I", "UP"]
    """)

    files[".env"] = textwrap.dedent(f"""\
        DATABASE_URL=sqlite+aiosqlite:///./dev.db
        SECRET_KEY=change-me-before-production
        APP_NAME={project_name}
    """)

    files["alembic.ini"] = textwrap.dedent(f"""\
        [alembic]
        script_location = alembic
        sqlalchemy.url = sqlite:///./dev.db

        [loggers]
        keys = root,sqlalchemy,alembic

        [handlers]
        keys = console

        [formatters]
        keys = generic

        [logger_root]
        level = WARN
        handlers = console
        qualname =

        [logger_sqlalchemy]
        level = WARN
        handlers =
        qualname = sqlalchemy.engine

        [logger_alembic]
        level = INFO
        handlers =
        qualname = alembic

        [handler_console]
        class = StreamHandler
        args = (sys.stderr,)
        level = NOTSET
        formatter = generic

        [formatter_generic]
        format = %(levelname)-5.5s [%(name)s] %(message)s
        datefmt = %H:%M:%S
    """)

    files["alembic/env.py"] = textwrap.dedent(f"""\
        import asyncio
        from logging.config import fileConfig

        from alembic import context
        from sqlalchemy.ext.asyncio import create_async_engine

        from {package_name}.db import DATABASE_URL
        from {package_name}.models import SQLModel  # noqa: F401 — import all models

        config = context.config
        if config.config_file_name is not None:
            fileConfig(config.config_file_name)

        target_metadata = SQLModel.metadata


        def run_migrations_offline() -> None:
            context.configure(
                url=DATABASE_URL,
                target_metadata=target_metadata,
                literal_binds=True,
                dialect_opts={{"paramstyle": "named"}},
            )
            with context.begin_transaction():
                context.run_migrations()


        async def run_migrations_online() -> None:
            connectable = create_async_engine(DATABASE_URL)
            async with connectable.connect() as connection:
                await connection.run_sync(
                    lambda conn: context.configure(
                        connection=conn,
                        target_metadata=target_metadata,
                    )
                )
                async with connection.begin():
                    await connection.run_sync(lambda _: context.run_migrations())


        if context.is_offline_mode():
            run_migrations_offline()
        else:
            asyncio.run(run_migrations_online())
    """)

    files["alembic/versions/.gitkeep"] = ""

    files[f"src/{package_name}/__init__.py"] = ""

    files[f"src/{package_name}/main.py"] = textwrap.dedent(f"""\
        from contextlib import asynccontextmanager
        from typing import AsyncGenerator

        from fastapi import FastAPI

        from {package_name}.db import create_db_tables
        from {package_name}.routers import health, items


        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
            await create_db_tables()
            yield


        app = FastAPI(title="{project_name}", lifespan=lifespan)
        app.include_router(health.router)
        app.include_router(items.router)
    """)

    files[f"src/{package_name}/db.py"] = textwrap.dedent(f"""\
        from typing import AsyncGenerator

        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
        from sqlalchemy.orm import sessionmaker
        from sqlmodel import SQLModel

        from {package_name}.settings import settings

        DATABASE_URL: str = settings.database_url

        engine = create_async_engine(DATABASE_URL, echo=False)

        AsyncSessionLocal = sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )


        async def create_db_tables() -> None:
            async with engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)


        async def get_session() -> AsyncGenerator[AsyncSession, None]:
            async with AsyncSessionLocal() as session:
                yield session
    """)

    files[f"src/{package_name}/settings.py"] = textwrap.dedent(f"""\
        from pydantic_settings import BaseSettings, SettingsConfigDict


        class Settings(BaseSettings):
            model_config = SettingsConfigDict(env_file=".env", extra="forbid")

            database_url: str
            secret_key: str
            app_name: str


        settings = Settings()
    """)

    files[f"src/{package_name}/models.py"] = textwrap.dedent("""\
        from typing import Optional

        from sqlmodel import Field, SQLModel


        class ItemBase(SQLModel):
            name: str
            description: Optional[str] = None


        class Item(ItemBase, table=True):
            id: Optional[int] = Field(default=None, primary_key=True)
    """)

    files[f"src/{package_name}/schemas.py"] = textwrap.dedent("""\
        from typing import Optional

        from sqlmodel import SQLModel


        class ItemCreate(SQLModel):
            name: str
            description: Optional[str] = None


        class ItemUpdate(SQLModel):
            name: Optional[str] = None
            description: Optional[str] = None


        class ItemRead(SQLModel):
            id: int
            name: str
            description: Optional[str] = None
    """)

    files[f"src/{package_name}/routers/__init__.py"] = ""

    files[f"src/{package_name}/routers/health.py"] = textwrap.dedent(f"""\
        from fastapi import APIRouter, Depends
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy import text

        from {package_name}.db import get_session

        router = APIRouter()


        @router.get("/health")
        async def health(session: AsyncSession = Depends(get_session)) -> dict:
            await session.execute(text("SELECT 1"))
            return {{"status": "ok", "db": "ok"}}
    """)

    files[f"src/{package_name}/routers/items.py"] = textwrap.dedent(f"""\
        from typing import List

        from fastapi import APIRouter, Depends, HTTPException
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlmodel import select

        from {package_name}.db import get_session
        from {package_name}.models import Item
        from {package_name}.schemas import ItemCreate, ItemRead, ItemUpdate

        router = APIRouter(prefix="/items", tags=["items"])


        @router.post("/", response_model=ItemRead, status_code=201)
        async def create_item(
            payload: ItemCreate,
            session: AsyncSession = Depends(get_session),
        ) -> Item:
            item = Item.model_validate(payload)
            session.add(item)
            await session.commit()
            await session.refresh(item)
            return item


        @router.get("/", response_model=List[ItemRead])
        async def list_items(session: AsyncSession = Depends(get_session)) -> List[Item]:
            result = await session.execute(select(Item))
            return result.scalars().all()


        @router.get("/{{item_id}}", response_model=ItemRead)
        async def get_item(
            item_id: int,
            session: AsyncSession = Depends(get_session),
        ) -> Item:
            item = await session.get(Item, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return item


        @router.patch("/{{item_id}}", response_model=ItemRead)
        async def update_item(
            item_id: int,
            payload: ItemUpdate,
            session: AsyncSession = Depends(get_session),
        ) -> Item:
            item = await session.get(Item, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            update_data = payload.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(item, key, value)
            session.add(item)
            await session.commit()
            await session.refresh(item)
            return item


        @router.delete("/{{item_id}}", status_code=204)
        async def delete_item(
            item_id: int,
            session: AsyncSession = Depends(get_session),
        ) -> None:
            item = await session.get(Item, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            await session.delete(item)
            await session.commit()
    """)

    files["tests/conftest.py"] = textwrap.dedent(f"""\
        import pytest
        from httpx import ASGITransport, AsyncClient
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
        from sqlalchemy.orm import sessionmaker
        from sqlmodel import SQLModel

        from {package_name}.db import get_session
        from {package_name}.main import app

        TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


        @pytest.fixture
        async def session() -> AsyncSession:
            engine = create_async_engine(TEST_DATABASE_URL)
            async with engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)
            async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            async with async_session() as s:
                yield s
            async with engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.drop_all)


        @pytest.fixture
        async def client(session: AsyncSession) -> AsyncClient:
            app.dependency_overrides[get_session] = lambda: session
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as c:
                yield c
            app.dependency_overrides.clear()
    """)

    files["tests/test_health.py"] = textwrap.dedent("""\
        import pytest
        from httpx import AsyncClient


        @pytest.mark.asyncio
        async def test_health(client: AsyncClient) -> None:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            assert data["db"] == "ok"
    """)

    # ── Write all files ──────────────────────────────────────────────────────
    for rel_path, content in files.items():
        full_path = target / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        print(f"  created {rel_path}")


if __name__ == "__main__":
    main()
