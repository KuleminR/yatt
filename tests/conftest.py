import asyncio
import pytest
from typing import AsyncIterable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from httpx import ASGITransport, AsyncClient

from yatt.core import Base, get_db_session
from yatt.main import app

# Setup test db
_test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")


async def init_tables():
    async with _test_engine.begin() as c:
        await c.run_sync(Base.metadata.create_all)


asyncio.run(init_tables())


_session_factory = async_sessionmaker(_test_engine, expire_on_commit=False)


async def test_db_session() -> AsyncIterable[AsyncSession]:
    async with _session_factory() as session:
        yield session


app.dependency_overrides[get_db_session] = test_db_session


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://localhost:8000",
        follow_redirects=True,
    ) as ac:
        yield ac


@pytest.fixture
async def db_session() -> AsyncIterable[AsyncSession]:
    async with _session_factory() as session:
        yield session
