from fastapi.exceptions import HTTPException
import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from starlette.status import HTTP_201_CREATED
from app.models.product import ProductInDB

from app.models.user import UserInDB
from app.models.item import Size, ItemCreate, WhatDo

pytestmark = pytest.mark.asyncio

class TestUserProductCreate:
    async def test_users_can_create_item(self, app: FastAPI, authorized_client: AsyncClient, test_user: UserInDB, test_product:ProductInDB) -> None:
        new_item = ItemCreate(
            user_id = test_user.id,
            product_id = test_product.id,
            what_do = "trade",
        )
        print("before post")
        print(str(new_item.dict()))

        res = await authorized_client.post(
            app.url_path_for("items:create-item"), json={"new_item":new_item.dict()}
        )
        assert res.status_code == HTTP_201_CREATED

        created_item = ItemCreate(**res.json())
        assert created_item == new_item