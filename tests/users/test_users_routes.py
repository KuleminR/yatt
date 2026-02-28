import pytest
from uuid import uuid7

from httpx import AsyncClient
from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from yatt.users.models import User
from yatt.utils import verify_password


class TestCreateRoute:
    @pytest.mark.anyio
    async def test_successful_create_user(self, client: AsyncClient):
        successful_request_data = {
            "login": "test_user",
            "email": "test@example.com",
            "password": "q123",
        }

        response = await client.post("/users", json=successful_request_data)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert list(response_data.keys()) == ["login", "email", "uuid"]
        assert response_data["login"] == "test_user"
        assert response_data["email"] == "test@example.com"

    @pytest.mark.anyio
    async def test_no_mandatory_field_error(self, client: AsyncClient):
        no_mandatory_field_request_data = {
            "email": "test@example.com",
        }

        no_mandatory_field_response_data = {
            "errors": [
                {
                    "type": "validation_error",
                    "msg": "Field required",
                    "details": {"loc": "body.login"},
                },
                {
                    "type": "validation_error",
                    "msg": "Field required",
                    "details": {"loc": "body.password"},
                },
            ]
        }

        response = await client.post("/users", json=no_mandatory_field_request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json() == no_mandatory_field_response_data

    @pytest.mark.anyio
    async def test_input_fields_format(self, client: AsyncClient):
        no_mandatory_field_request_data = {
            "email": "test@example.com",
            "password": 123,
            "login": True,
        }

        no_mandatory_field_response_data = {
            "errors": [
                {
                    "type": "validation_error",
                    "msg": "Input should be a valid string",
                    "details": {"loc": "body.login"},
                },
                {
                    "type": "validation_error",
                    "msg": "Input should be a valid string",
                    "details": {"loc": "body.password"},
                },
            ]
        }

        response = await client.post("/users", json=no_mandatory_field_request_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json() == no_mandatory_field_response_data

    @pytest.mark.anyio
    async def test_user_already_exists(self, client: AsyncClient, existing_user: User):
        existing_user_request_data = {
            "login": existing_user.login,
            "email": existing_user.email,
            "password": existing_user.password,
        }

        expected_response = {
            "detail": f"User with name {existing_user.login} already exists"
        }

        response = await client.post("/users", json=existing_user_request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == expected_response


class TestGetUserRoute:
    @pytest.mark.anyio
    async def test_succesfully_get_user(self, client: AsyncClient, existing_user: User):
        expected_response = {
            "uuid": str(existing_user.uuid),
            "login": existing_user.login,
            "email": existing_user.email,
        }

        response = await client.get(f"/users/{existing_user.uuid}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_response

    @pytest.mark.anyio
    async def test_user_not_found(self, client: AsyncClient):
        non_existend_user_uuid = str(uuid7())
        expected_response = {"detail": f"User {non_existend_user_uuid} not found"}

        response = await client.get(f"/users/{non_existend_user_uuid}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == expected_response


class TestChangePasswordRoute:
    @pytest.mark.anyio
    async def test_successfully_change_password(
        self, client: AsyncClient, db_session: AsyncSession, existing_user: User
    ):
        successful_request_data = {"password": "new_password"}

        response = await client.post(
            f"/users/{str(existing_user.uuid)}/change_password",
            json=successful_request_data,
        )

        await db_session.refresh(existing_user)

        assert response.status_code == status.HTTP_200_OK
        assert verify_password(
            successful_request_data["password"], existing_user.password
        )


class TestDeleteUserRoute:
    @pytest.mark.anyio
    async def test_successfully_delete_user(
        self, client: AsyncClient, existing_user: User, db_session: AsyncSession
    ):
        response = await client.delete(f"/users/{str(existing_user.uuid)}")

        user_in_db = await db_session.scalars(
            select(User).where(User.uuid == existing_user.uuid)
        )

        assert response.status_code == status.HTTP_200_OK
        assert user_in_db.one_or_none() is None


class TestPatchUser:
    @pytest.mark.anyio
    async def test_successfully_patch_user(
        self, client: AsyncClient, existing_user: User, db_session: AsyncSession
    ):
        successful_user_patch_request = {"email": "changed_user_email@example.com"}

        expected_response = {
            "uuid": str(existing_user.uuid),
            "login": existing_user.login,
            "email": successful_user_patch_request["email"],
        }

        response = await client.patch(
            f"/users/{str(existing_user.uuid)}", json=successful_user_patch_request
        )

        await db_session.refresh(existing_user)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_response
        assert existing_user.email == successful_user_patch_request["email"]
