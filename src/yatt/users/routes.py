from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from yatt.core import DBSession
from yatt.users.models import (
    UserCreateParams,
    UserPatchParams,
    UserSetPasswordParams,
    UserView,
)

import yatt.users.service as service

auth_router = APIRouter(prefix="/auth", tags=["authentication"])
users_router = APIRouter(prefix="/users", tags=["users"])


@auth_router.post("/{user_uuid}/login", response_model=UserView)
async def login_user(user_uuid: UUID, db_session: DBSession):
    pass


@users_router.post("/", response_model=UserView)
async def register_user(params: UserCreateParams, db_session: DBSession):
    existing_user = await service.get_by_login(db_session, params.login)

    if existing_user is not None:
        raise HTTPException(
            status_code=400, detail=f"User with name {params.login} already exists"
        )

    user = await service.create(db_session, params)

    return user


@users_router.get("/{user_uuid}", response_model=UserView)
async def get_user(user_uuid: UUID, db_session: DBSession):
    user = await service.get_by_uuid(db_session, user_uuid)

    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_uuid} not found")

    return user


@users_router.patch("/{user_uuid}", response_model=UserView)
async def update_user(user_uuid: UUID, params: UserPatchParams, db_session: DBSession):
    user = await service.get_by_uuid(db_session, user_uuid)

    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_uuid} not found")

    updated_user = await service.patch(db_session, user, params)

    return updated_user


@users_router.post("/{user_uuid}/change_password", status_code=status.HTTP_200_OK)
async def set_password(
    user_uuid: UUID, params: UserSetPasswordParams, db_session: DBSession
):
    user = await service.get_by_uuid(db_session, user_uuid)

    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_uuid} not found")

    await service.change_password(db_session, user, params.password)


@users_router.delete("/{user_uuid}", status_code=status.HTTP_200_OK)
async def delete_user(user_uuid: UUID, db_session: DBSession):
    user = await service.get_by_uuid(db_session, user_uuid)

    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_uuid} not found")

    await service.delete(db_session, user)
