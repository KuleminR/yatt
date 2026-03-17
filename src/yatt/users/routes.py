from datetime import timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from yatt.core import DBSession
import yatt.users.service as service
from yatt.users.models import (
    UserCreateParams,
    UserPatchParams,
    UserSetPasswordParams,
    UserView,
)
import yatt.auth.service as auth_service
from yatt.auth.models import Token
from yatt.auth.dependencies import get_verified_access_token


users_router = APIRouter(prefix="/users")

protected_router = APIRouter(
    tags=["users"],
    dependencies=[Depends(get_verified_access_token)],
)

public_router = APIRouter(tags=["users"])


@public_router.post("/login", response_model=Token)
async def login_user(
    db_session: DBSession, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await service.authenticate_user(
        db_session, form_data.username, form_data.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    access_token = auth_service.create_access_token(
        user_identity=user.uuid, expires_in=timedelta(hours=2), permissions=[""]
    )

    return {"access_token": access_token, "type": "bearer"}


@public_router.post("/", response_model=UserView)
async def register_user(params: UserCreateParams, db_session: DBSession):
    existing_user = await service.get_by_login(db_session, params.login)

    if existing_user is not None:
        raise HTTPException(
            status_code=400, detail=f"User with name {params.login} already exists"
        )

    user = await service.create(db_session, params)

    return user


@protected_router.get("/{user_uuid}", response_model=UserView)
async def get_user(user_uuid: UUID, db_session: DBSession):
    user = await service.get_by_uuid(db_session, user_uuid)

    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_uuid} not found")

    return user


@protected_router.patch("/{user_uuid}", response_model=UserView)
async def update_user(user_uuid: UUID, params: UserPatchParams, db_session: DBSession):
    user = await service.get_by_uuid(db_session, user_uuid)

    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_uuid} not found")

    updated_user = await service.patch(db_session, user, params)

    return updated_user


@protected_router.post("/{user_uuid}/change_password", status_code=status.HTTP_200_OK)
async def set_password(
    user_uuid: UUID, params: UserSetPasswordParams, db_session: DBSession
):
    user = await service.get_by_uuid(db_session, user_uuid)

    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_uuid} not found")

    await service.change_password(db_session, user, params.password)


@protected_router.delete("/{user_uuid}", status_code=status.HTTP_200_OK)
async def delete_user(user_uuid: UUID, db_session: DBSession):
    user = await service.get_by_uuid(db_session, user_uuid)

    if user is None:
        raise HTTPException(status_code=404, detail=f"User {user_uuid} not found")

    await service.delete(db_session, user)


users_router.include_router(protected_router)
users_router.include_router(public_router)
