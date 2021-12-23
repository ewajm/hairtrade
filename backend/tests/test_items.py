from typing import List
from fastapi.exceptions import HTTPException
import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.orm import session
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from app.api.routes.products import create_new_product
from app.db.metadata import Item
from app.db.repositories.items import ItemRepository
from app.models.product import ProductInDB, ProductType

from app.models.user import UserInDB
from app.models.item import ItemInDB, ItemPublic, ItemPublicByProduct, ItemPublicByUser, Size, ItemCreate, WhatDo

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def test_item(test_user:UserInDB, test_product:ProductInDB, db:session.Session):
    new_item = ItemCreate(
        user_id = test_user.id,
        product_id = test_product.id,
        what_do = WhatDo.trade,
        comment = "didn't like smell",
        size = Size.travel
    )
    existing_item = db.query(Item).filter(
        Item.user_id == test_user.id, 
        Item.product_id == test_product.id,
        Item.what_do == "trade",
        Item.comment == "didn't like smell",
        Item.size == "travel",
    ).first()
    if existing_item:
        return existing_item
    item_repo = ItemRepository(db)
    return item_repo.create_item(item_create= new_item)

@pytest.fixture
async def test_item2(test_user2:UserInDB, test_product:ProductInDB, db:session.Session):
    new_item = ItemCreate(
        user_id = test_user2.id,
        product_id = test_product.id,
        what_do = WhatDo.giveaway,
        comment = "doesn't work for me",
        size = Size.jumbo
    )
    existing_item = db.query(Item).filter(
        Item.user_id == test_user2.id, 
        Item.product_id == test_product.id,
        Item.what_do == "give away",
        Item.comment == "doesn't work for me",
        Item.size == "jumbo",
    ).first()
    if existing_item:
        return existing_item
    item_repo = ItemRepository(db)
    return item_repo.create_item(item_create= new_item)

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

    @pytest.mark.parametrize(
        "invalid_payload, status_code",
        (
            (None, 422),
            ({}, 422),
            ({"user_id": 1}, 422),
            ({"user_id": 1, "what_do": "trade"}, 422),
            ({"product_id": 1, "comment": "test"}, 422),
            ({"size": "jumbo", "what_do": "trade", "comment": "test"}, 422),
            ({"comment": "test", "size": "jumbo", "price": 400}, 422),
        ),
    )
    async def test_invalid_input_raises_error(
        self, app:FastAPI, authorized_client: AsyncClient, invalid_payload:dict,status_code:int
    ) -> None:
        res = await authorized_client.post(
            app.url_path_for("items:create-item"),json={"new_item":invalid_payload}
        )
        assert res.status_code == status_code

class TestGetItem:
   
    async def test_item_can_be_retrieved_by_id(self, app:FastAPI, client: AsyncClient, test_item:ItemInDB)-> None:
        res = await client.get(app.url_path_for("items:get-item-by-id", id=test_item.id))
        returned_item = ItemPublic(**res.json())
        assert ItemPublic.from_orm(test_item) == returned_item

    @pytest.mark.parametrize(
        "id, status_code",
        (
            (999,404),
            (-1, 422),
            (None, 422),
        )
    )
    async def test_wrong_id_returns_error(
        self, app:FastAPI, client:AsyncClient, id:int, status_code:int
    ) -> None:
        res = await client.get(app.url_path_for("items:get-item-by-id", id=id))
        assert res.status_code == status_code

    async def test_items_can_be_retrieved_by_user(self, app:FastAPI, client: AsyncClient,test_item:ItemInDB, test_user:UserInDB, test_product: ProductInDB, db:session.Session) -> None:
        nu_item_create2 = ItemCreate(
            user_id = test_user.id,
            product_id = test_product.id,
            what_do = WhatDo.giveaway,
            size = Size.sample
        )
        item_repo = ItemRepository(db)
        nu_item1 = ItemPublicByUser.from_orm(item_repo.create_item(item_create = nu_item_create2)) 
        res = await client.get(app.url_path_for("items:get-items-by-user", user_id = test_user.id))
        items = [ItemPublicByUser(**l) for l in res.json()] 
        assert ItemPublicByUser.from_orm(test_item) in items
        assert nu_item1 in items   

    @pytest.mark.parametrize(
        "user_id, status_code",
        (
            (999,404),
            (-1, 422),
            (None, 422),
        )
    )
    async def test_wrong_user_id_returns_error(
        self, app:FastAPI, client:AsyncClient, user_id:int, status_code:int
    ) -> None:
        res = await client.get(app.url_path_for("items:get-items-by-user", user_id=user_id))
        assert res.status_code == status_code

    async def test_items_can_be_retrieved_by_product(self, app:FastAPI, client: AsyncClient, test_item:ItemInDB, test_user:UserInDB, test_product: ProductInDB, db:session.Session) -> None:
        nu_item_create2 = ItemCreate(
            user_id = test_user.id,
            product_id = test_product.id,
            what_do = WhatDo.giveaway,
            size = Size.sample
        )
        item_repo = ItemRepository(db)
        nu_item1 = ItemPublicByProduct.from_orm(item_repo.create_item(item_create = nu_item_create2)) 
        res = await client.get(app.url_path_for("items:get-items-by-product", product_id = test_product.id))
        items = [ItemPublicByProduct(**l) for l in res.json()] 
        assert ItemPublicByProduct.from_orm(test_item) in items
        assert nu_item1 in items   

    @pytest.mark.parametrize(
        "product_id, status_code",
        (
            (999,404),
            (-1, 422),
            (None, 422),
        )
    )
    async def test_wrong_product_id_returns_error(
        self, app:FastAPI, client:AsyncClient, product_id:int, status_code:int
    ) -> None:
        res = await client.get(app.url_path_for("items:get-items-by-product", product_id=product_id))
        assert res.status_code == status_code

    async def test_all_items_can_be_retrieved(self, app:FastAPI, client:AsyncClient) -> None:
        res = await client.get(app.url_path_for("items:get-all-items"))
        assert res.status_code == HTTP_200_OK
        assert isinstance(res.json(), list)
        assert len(res.json()) > 0

class TestUpdateItem:
    @pytest.mark.parametrize(
        "attrs_to_change, values",
        (
            (["what_do"],["give away"]),
            (["comment"],["too heavy for my hair"]),
            (["size"], ["jumbo"]),
            (
                ["what_do", "price"],
                [
                    "sell",
                    400,
                ],
            ),
        ),
    )
    async def test_update_item_with_valid_input(
        self,
        app:FastAPI,
        authorized_client: AsyncClient,
        test_item: Item,
        attrs_to_change: List[str],
        values: List[str],
    ) -> None:
        item_update = {
            "item_update": {
                attrs_to_change[i]: values[i] for i in range(len(attrs_to_change))
            }
        }
        res = await authorized_client.put(
            app.url_path_for(
                "items:update-item-by-id",
                id=test_item.id,
            ),
            json = item_update
        )
        assert res.status_code == HTTP_200_OK
        updated_item = ItemPublic(**res.json())
        assert updated_item.id == test_item.id  # make sure it's the same cleaning
        # make sure that any attribute we updated has changed to the correct value
        target_item = ItemPublic.from_orm(test_item)
        print(updated_item)
        print(target_item)
        for i in range(len(attrs_to_change)):
            attr_to_change = getattr(updated_item, attrs_to_change[i])
            assert attr_to_change != getattr(test_item, attrs_to_change[i])
            assert attr_to_change == values[i] 
        # make sure that no other attributes' values have changed
        
        for attr, value in updated_item.dict().items():
            if attr not in attrs_to_change and attr != "updated_at":
                assert getattr(target_item, attr) == value

    @pytest.mark.parametrize(
        "id, payload, status_code",
        (
            (-1, {"comment": "test"}, 422),
            (0, {"comment": "test2"}, 422),
            (500, {"comment": "test3"}, 404),
            (1, None, 422),
            (1, {"what_do": "invalid what_do"}, 422),
            (1, {"size": None}, 400),
        ),
    )
    async def test_update_item_with_invalid_input_throws_error(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
        id: int,
        payload: dict,
        status_code: int,
    ) -> None:
        item_update = {"item_update": payload}
        res = await authorized_client.put(
            app.url_path_for("items:update-item-by-id", id=id),
            json=item_update
        )
        assert res.status_code == status_code

class TestDeleteItem:
    async def test_item_can_be_deleted(self, app:FastAPI, authorized_client: AsyncClient, test_item:ItemInDB)-> None:
        res = await authorized_client.delete(app.url_path_for("items:delete-item-by-id", id=test_item.id))
        assert res.status_code == HTTP_200_OK
        # ensure that the item no longer exists
        res = await authorized_client.get(
            app.url_path_for(
                "items:get-item-by-id", 
                id=test_item.id,
            ),
        )
        assert res.status_code == HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "id, status_code",
        (
            (999,404),
            (-1, 422),
            (None, 422),
        )
    )
    async def test_wrong_id_returns_error(
        self, app:FastAPI, client:AsyncClient, id:int, status_code:int
    ) -> None:
        res = await client.get(app.url_path_for("items:delete-item-by-id", id=id))
        assert res.status_code == status_code

    async def test_item_cannot_be_deleted_if_not_logged_in(self, app:FastAPI, client: AsyncClient, test_item:ItemInDB)-> None:
        res = await client.delete(app.url_path_for("items:delete-item-by-id", id=test_item.id))
        assert res.status_code == HTTP_401_UNAUTHORIZED
        self.test_item_id = None

    async def test_authenticated_users_cannot_delete_items_for_other_users(self, app: FastAPI, authorized_client: AsyncClient, test_item2:ItemInDB) -> None:
        res = await authorized_client.delete(app.url_path_for("items:delete-item-by-id", id=test_item2.id))
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        assert res.json() == {"detail": "Cannot delete products for other users"}
        self.test_item_id = None