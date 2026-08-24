"""
pytest-Fixtures fuer die Backend-Tests.

Verwendet SQLite In-Memory (aiosqlite) statt Postgres,
damit die Tests ohne Docker laufen.
"""
from __future__ import annotations

import os

# backend.core.config.Settings() verlangt DATABASE_URL/SECRET_KEY/
# ENCRYPTION_KEY hart (Phase A, kein "changeme"-Fallback mehr) und wird
# beim ersten Import von backend.core.database/backend.main ausgewertet -
# muss deshalb VOR jedem backend-Import gesetzt sein. os.environ.setdefault,
# damit eine echte .env (z.B. lokal via pytest-dotenv) Vorrang behaelt.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "pytest-only-secret-key-not-used-in-production")
if "ENCRYPTION_KEY" not in os.environ:
    from cryptography.fernet import Fernet
    os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()

import httpx
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.database import Base, get_db

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncSession:  # type: ignore[override]
    """Erzeugt eine frische In-Memory-DB pro Testfunktion."""
    engine = create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession, tmp_path, monkeypatch):  # type: ignore[override]
    """HTTP-Client fuer echte Endpunkt-Tests gegen die FastAPI-App.

    httpx.AsyncClient mit ASGITransport statt Starlette-TestClient: teilt
    sich das Event-Loop mit dem "db"-Fixture und dem Testfall selbst (beide
    async def unter pytest-asyncio) - der synchrone TestClient laeuft
    intern in einem eigenen Loop, was mit einer async SQLAlchemy-Session
    zu "Future attached to a different loop"-Fehlern fuehrt.
    """
    from backend.main import app
    import backend.api.cv as cv_module

    async def _override_get_db():
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    monkeypatch.setattr(cv_module, "UPLOAD_DIR", str(tmp_path))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
