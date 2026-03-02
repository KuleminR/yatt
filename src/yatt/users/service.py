import logging
from uuid import UUID, uuid7
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from yatt.users.models import Password, User, UserCreateParams, UserPatchParams
from yatt.utils import hash_password


logger = logging.getLogger(__name__)


async def create(db_session: AsyncSession, user_create: UserCreateParams) -> User:
    """Create new user"""

    uuid = uuid7()

    hashed_password = hash_password(user_create.password)

    new_user = User(
        uuid=uuid,
        login=user_create.login,
        email=user_create.email,
        password=hashed_password,
    )

    db_session.add(new_user)

    await db_session.commit()
    return new_user


async def get_by_uuid(db_session: AsyncSession, user_uuid: UUID) -> User | None:
    """Get user by UUID"""

    stmt = select(User).where(User.uuid == user_uuid)

    result = await db_session.scalars(stmt)
    return result.one_or_none()


async def get_by_login(db_session: AsyncSession, login: str) -> User | None:
    stmt = select(User).where(User.login == login)

    result = await db_session.scalars(stmt)
    return result.one_or_none()


async def patch(
    db_session: AsyncSession, user: User, user_patch: UserPatchParams
) -> User | None:
    """Update existing user"""

    user_patch_data = user_patch.model_dump(exclude_unset=True)
    user.patch(**user_patch_data)

    await db_session.commit()
    return user


async def change_password(db_session: AsyncSession, user: User, new_password: Password):
    """Change password for given user"""

    user.password = hash_password(new_password)

    await db_session.commit()


async def delete(db_session: AsyncSession, user: User):
    """Delete user"""

    await db_session.delete(user)

    await db_session.commit()
