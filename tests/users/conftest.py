import pytest
from uuid import uuid7

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from yatt.users.models import User
from yatt.utils import hash_password


@pytest.fixture
async def existing_user(db_session: AsyncSession):
    user = User(
        uuid=uuid7(),
        login="existing_user",
        email="existing@example.com",
        password=hash_password("q123"),
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    yield user

    updated_user = await db_session.scalars(select(User).where(User.uuid == user.uuid))

    if updated_user.one_or_none() is not None:
        await db_session.delete(user)
        await db_session.commit()
