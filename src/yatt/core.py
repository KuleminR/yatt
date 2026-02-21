from typing import Annotated, AsyncIterator

from fastapi import Depends
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from yatt.config import DBConfig, db_config


class Base(AsyncAttrs, DeclarativeBase):
    def patch(self, **kwargs):
        """Method for model patching"""

        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)


def get_db_url(config: DBConfig) -> str:
    return f"postgresql+asyncpg://{config.user}:{config.password}@{config.hostname}:{config.port}/{config.name}"


def generate_engine(config: DBConfig) -> AsyncEngine:
    """Create configured database engine"""
    string_url = get_db_url(config)

    url = make_url(string_url)

    return create_async_engine(url)


_engine = generate_engine(db_config)

_session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with _session_factory() as session:
        yield session


DBSession = Annotated[AsyncSession, Depends(get_db_session)]
