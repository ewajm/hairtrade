
from typing import List
import pytest
from httpx import AsyncClient
from fastapi import FastAPI

from starlette.status  import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_201_CREATED

from app.models.product import ProductCreate
from app.models.product import ProductType
from app.models.product import WhatDo
from app.models.product import ProductPublic
from app.db.metadata import Product  
# decorate all tests with @pytest.mark.asyncio
pytestmark = pytest.mark.asyncio  

@pytest.fixture
def new_product():
    return ProductCreate(
        product_name="test_product",
        description="test description",
        type=ProductType.cream,
        brand="test brand",
        what_do=WhatDo.trade,
        price=0.00
    )

class TestProductsRoutes:
    async def test_routes_exist(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(app.url_path_for("products:create-product"), json={})
        assert res.status_code != HTTP_404_NOT_FOUND

    async def test_invalid_input_raises_errors(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(app.url_path_for("products:create-product"), json={})
        assert res.status_code == HTTP_422_UNPROCESSABLE_ENTITY

class TestCreateProduct:
    async def test_valid_input_creates_cleaning(
        self, app:FastAPI, client:AsyncClient, new_product: ProductCreate
    ) -> None:
        res = await client.post(
            app.url_path_for("products:create-product"),json={"new_product":new_product.dict()}
        )
        assert res.status_code == HTTP_201_CREATED

        created_product = ProductCreate(**res.json())
        assert created_product == new_product

    @pytest.mark.parametrize(
        "invalid_payload, status_code",
        (
            (None, 422),
            ({}, 422),
            ({"product_name": "test_name"}, 422),
            ({"price": 10.00}, 422),
            ({"product_name:": "test_name", "description": "test"}, 422),
            ({"product_name:": "test_name", "type": ProductType.dunno}, 422),
            ({"product_name:": "test_name", "what_do": WhatDo.trade}, 422),
            ({"description:": "test_name", "type": ProductType.dunno}, 422),
        ),
    )
    async def test_invalid_input_raises_error(
        self, app:FastAPI, client: AsyncClient, invalid_payload:dict,status_code:int
    ) -> None:
        res = await client.post(
            app.url_path_for("products:create-product"),json={"new_product":invalid_payload}
        )
        assert res.status_code == status_code
        
class TestGetProduct:
    async def test_get_product_by_id(
        self, app:FastAPI, client:AsyncClient, test_product:Product
    ) -> None:
        res = await client.get(app.url_path_for("products:get-product-by-id",id=test_product.id))
        assert res.status_code == HTTP_200_OK
        product = ProductPublic(**res.json())
        assert product == ProductPublic.from_orm(test_product)

    @pytest.mark.parametrize(
        "id, status_code",
        (
            (999,404),
            (-1, 404),
            (None, 422),
        )
    )
    async def test_wrong_id_returns_error(
        self, app:FastAPI, client:AsyncClient, id:int, status_code:int
    ) -> None:
        res = await client.get(app.url_path_for("products:get-product-by-id",id=id))
        assert res.status_code == status_code

    async def test_get_all_products_returns_valid_response(
        self, app: FastAPI, client: AsyncClient, test_product: Product
    ) -> None:
        res = await client.get(app.url_path_for("products:get-all-products"))
        assert res.status_code == HTTP_200_OK
        assert isinstance(res.json(), list)
        assert len(res.json()) > 0        
        products = [ProductPublic(**l) for l in res.json()]
        assert ProductPublic.from_orm(test_product) in products

class TestUpdateProduct:
    @pytest.mark.parametrize(
        "attrs_to_change, values",
        (
            (["product_name"], ["new fake product name"]),
            (["description"], ["new fake product description"]),
            (["price"], [3.14]),
            (["type"], ["gel"]),            
            (
                ["product_name", "brand"], 
                [
                    "extra new fake product name", 
                    "extra new fake product brand",
                ],
            ),
            (["what_do", "type"], ["give away", "oil"]),
        ),
    )
    async def test_update_product_with_valid_input(
        self, 
        app: FastAPI, 
        client: AsyncClient, 
        test_product: Product, 
        attrs_to_change: List[str], 
        values: List[str],
    ) -> None:
        product_update = {
            "product_update": {
                attrs_to_change[i]: values[i] for i in range(len(attrs_to_change))
            }
        }
        res = await client.put(
            app.url_path_for(
                "products:update-product-by-id",
                id=test_product.id,
            ),
            json=product_update
        )
        assert res.status_code == HTTP_200_OK
        updated_product = ProductPublic(**res.json())
        assert updated_product.id == test_product.id  # make sure it's the same cleaning
        # make sure that any attribute we updated has changed to the correct value
        for i in range(len(attrs_to_change)):
            attr_to_change = getattr(updated_product, attrs_to_change[i])
            assert attr_to_change != getattr(test_product, attrs_to_change[i])
            assert attr_to_change == values[i] 
        # make sure that no other attributes' values have changed
        test_product_obj = ProductPublic.from_orm(test_product)
        for attr, value in updated_product.dict().items():
            if attr not in attrs_to_change and attr != "updated_at":
                assert getattr(test_product_obj, attr) == value

    @pytest.mark.parametrize(
        "id, payload, status_code",
        (
            (-1, {"product_name": "test"}, 422),
            (0, {"product_name": "test2"}, 422),
            (500, {"product_name": "test3"}, 404),
            (1, None, 422),
            (1, {"type": "invalid product type"}, 422),
            (1, {"type": None}, 400),
            (1, {"what_do": "invalid what_do type"}, 422),
            (1, {"what_do": None}, 400),
        ),
    )
    async def test_update_cleaning_with_invalid_input_throws_error(
        self,
        app: FastAPI,
        client: AsyncClient,
        id: int,
        payload: dict,
        status_code: int,
    ) -> None:
        product_update = {"product_update": payload}
        res = await client.put(
            app.url_path_for("products:update-product-by-id", id=id),
            json=product_update
        )
        assert res.status_code == status_code

class TestDeleteProduct:
    async def test_can_delete_product_successfully(
        self,
        app: FastAPI,
        client: AsyncClient,
        test_product: Product,
    ) -> None:
        # delete the cleaning
        res = await client.delete(
            app.url_path_for(
                "products:delete-product-by-id", 
                id=test_product.id,
            ),
        )
        assert res.status_code == HTTP_200_OK
        # ensure that the cleaning no longer exists
        res = await client.get(
            app.url_path_for(
                "products:get-product-by-id", 
                id=test_product.id,
            ),
        )
        assert res.status_code == HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "id, status_code",
        (
            (500, 404),
            (0, 422),
            (-1, 422),
            (None, 422),
        ),
    )
    async def test_delete_cleaning_with_invalid_input_throws_error(
        self,
        app: FastAPI,
        client: AsyncClient,
        id: int,
        status_code: int,
    ) -> None:
        res = await client.delete(
            app.url_path_for("products:delete-product-by-id", id=id),
        )
        assert res.status_code == status_code  