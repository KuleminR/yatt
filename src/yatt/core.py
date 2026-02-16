from typing import Annotated
from fastapi import Depends
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import DeclarativeBase, Session

from yatt.config import DBConfig, db_config


class Base(DeclarativeBase):
    pass


def generate_engine(config: DBConfig) -> Engine:
    """Create configured database engine"""
    string_url = f"postgresql+psycopg2://{config.user}:{config.password}@{config.hostname}:{config.port}/{config.name}"

    url = make_url(string_url)

    return create_engine(url)


engine = generate_engine(db_config)


async def get_db_session():
    session = Session(engine)

    try:
        yield session
    finally:
        session.close()


DBSession = Annotated[Session, Depends(get_db_session)]
