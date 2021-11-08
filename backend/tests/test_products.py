from functools import total_ordering
import pytest
from httpx import AsyncClient
from fastapi import FastAPI

from starlette.status  import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_201_CREATED

from app.models.product import ProductCreate
from app.models.product import ProductType
from app.models.product import WhatDo
from app.models.product import ProductInDB
from tests.conftest import test_product  
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
        self, app:FastAPI, client:AsyncClient, test_product:ProductInDB
    ) -> None:
        res = await client.get(app.url_path_for("products:get-product-by-id",id=test_product.id))
        assert res.status_code == HTTP_200_OK
        product = ProductInDB(**res.json())
        assert product == test_product

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