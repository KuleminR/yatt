from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from yatt.core import DBSession
import yatt.users.service as service
from yatt.users.models import User
from yatt.auth.dependencies import get_verified_access_token
from yatt.auth.models import AccessToken


async def get_current_user(
    db_session: DBSession,
    token: Annotated[AccessToken, Depends(get_verified_access_token)],
) -> User:
    user_uuid = UUID(token.sub)

    user = await service.get_by_uuid(db_session, user_uuid)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    return user
