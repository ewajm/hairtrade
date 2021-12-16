from fastapi.exceptions import HTTPException
import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.orm import session
from starlette.status import HTTP_201_CREATED
from app.api.routes.products import create_new_product
from app.db.metadata import Item
from app.db.repositories.items import ItemRepository
from app.models.product import ProductInDB

from app.models.user import UserInDB
from app.models.item import ItemInDB, ItemPublic, ItemPublicByUser, Size, ItemCreate, WhatDo

pytestmark = pytest.mark.asyncio

class TestCreateItem:
    async def test_logged_in_users_can_create_item(self, app: FastAPI, authorized_client: AsyncClient, test_user: UserInDB, test_product:ProductInDB) -> None:
        new_item = ItemCreate(
            user_id = test_user.id,
            product_id = test_product.id,
            what_do = "trade",
        )
        res = await authorized_client.post(
            app.url_path_for("items:create-item"), json={"new_item":new_item.dict()}
        )
        assert res.status_code == HTTP_201_CREATED

        created_item = ItemCreate(**res.json())
        assert created_item == new_item

    async def test_unauthenticated_users_cannot_create_items(self, app: FastAPI, client: AsyncClient, test_user2: UserInDB, test_product:ProductInDB) -> None:
        new_item = ItemCreate(
            user_id = test_user2.id,
            product_id = test_product.id,
            what_do = "trade",
        )
        res = await client.post(
            app.url_path_for("items:create-item"), json={"new_item":new_item.dict()}
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_authenticated_users_cannot_create_items_for_other_users(self, app: FastAPI, authorized_client: AsyncClient, test_user:UserInDB, test_user2: UserInDB, test_product:ProductInDB) -> None:
        new_item = ItemCreate(
            user_id = test_user2.id,
            product_id = test_product.id,
            what_do = "trade",
        )
        res = await authorized_client.post(
            app.url_path_for("items:create-item"), json={"new_item":new_item.dict()}
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        assert res.json() == {"detail": "Cannot create products for other users"}

class TestGetItem:
    def create_new_product(self, *, user:UserInDB, product:ProductInDB, db:session.Session) -> ItemPublic:
        new_item = ItemCreate(
            user_id = user.id,
            product_id = product.id,
            what_do = "trade",
        )
        item_repo = ItemRepository(db)
        return item_repo.create_item(item_create = new_item)

    
    async def test_item_can_be_retrieved_by_id(self, app:FastAPI, authorized_client: AsyncClient, test_user:UserInDB, test_product:ProductInDB, db:session.Session)-> None:
        nu_item = ItemPublic.from_orm(self.create_new_product(user=test_user, product=test_product, db=db))
        res = await authorized_client.get(app.url_path_for("items:get-item-by-id", id=nu_item.id))
        returned_item = ItemPublic(**res.json())
        assert nu_item == returned_item

    async def test_items_can_be_retrieved_by_user(self, app:FastAPI, authorized_client: AsyncClient, test_user:UserInDB, test_product: ProductInDB, db:session.Session) -> None:
        nu_item = ItemPublicByUser.from_orm(self.create_new_product(user=test_user, product=test_product, db=db))
        nu_item_create2 = ItemCreate(
            user_id = test_user.id,
            product_id = test_product.id,
            what_do = WhatDo.giveaway,
            size = Size.sample
        )
        item_repo = ItemRepository(db)
        nu_item1 = ItemPublicByUser.from_orm(item_repo.create_item(item_create = nu_item_create2)) 
        res = await authorized_client.get(app.url_path_for("items:get-items-by-user", user_id = test_user.id))
        items = [ItemPublicByUser(**l) for l in res.json()] 
        assert nu_item in items
        assert nu_item1 in items    