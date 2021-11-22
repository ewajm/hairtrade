import pytest

from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.orm import session

from starlette.status import (
    HTTP_200_OK, 
    HTTP_201_CREATED, 
    HTTP_400_BAD_REQUEST, 
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND, 
    HTTP_422_UNPROCESSABLE_ENTITY,
)

from app.models.user import UserCreate, UserInDB
from app.db.repositories.users import UsersRepository


pytestmark = pytest.mark.asyncio


class TestUserRoutes:
    async def test_routes_exist(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(app.url_path_for("users:register-new-user"), json={})
        assert res.status_code != HTTP_404_NOT_FOUND

class TestUserRegistration:
    async def test_users_can_register_successfully(
        self, 
        app: FastAPI, 
        client: AsyncClient,
        db: session.Session,
    ) -> None:
        user_repo = UsersRepository(db)
        new_user = {"email": "shakira@shakira.io", "username": "shakirashakira", "password": "chantaje"}
        # make sure user doesn't exist yet
        user_in_db = user_repo.get_user_by_email(email=new_user["email"])
        assert user_in_db is None        
        # send post request to create user and ensure it is successful
        res = await client.post(app.url_path_for("users:register-new-user"), json={"new_user": new_user})
        assert res.status_code == HTTP_201_CREATED
        # ensure that the user now exists in the db
        user_in_db = user_repo.get_user_by_email(email=new_user["email"])
        assert user_in_db is not None
        assert user_in_db.email == new_user["email"]
        assert user_in_db.username == new_user["username"]
        # check that the user returned in the response is equal to the user in the database
        created_user = UserInDB(**res.json(), password="whatever", salt="123").dict(exclude={"password", "salt"})
        assert created_user == user_in_db.dict(exclude={"password", "salt"})