from fastapi.exceptions import HTTPException
import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from starlette.status import HTTP_201_CREATED
from app.models.product import ProductInDB

from app.models.user import UserInDB
from app.models.user_product import Size, UserProductCreate, WhatDo

pytestmark = pytest.mark.asyncio

class TestUserProductCreate:
    async def test_users_can_create_user_product(self, app: FastAPI, authorized_client: AsyncClient, test_user: UserInDB, test_product:ProductInDB) -> None:
        new_user_product = UserProductCreate(
            user_id = test_user.id,
            product_id = test_product.id,
            what_do = "trade",
        )
        print("before post")
        print(str(new_user_product.dict()))

        res = await authorized_client.post(
            app.url_path_for("user_products:create-user-product"), json={"new_user_product":new_user_product.dict()}
        )
        assert res.status_code == HTTP_201_CREATED

        created_user_product = UserProductCreate(**res.json())
        assert created_user_product == new_user_product