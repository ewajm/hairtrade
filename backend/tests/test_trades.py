from typing import List
from fastapi.exceptions import HTTPException
import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.orm import session
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from app.api.routes.products import create_new_product
from app.db.metadata import Trade
from app.db.repositories.trades import TradeRepository
from app.models.product import ProductInDB, ProductType

from app.models.user import UserInDB
from app.models.trade import TradeInDB, TradePublic, TradePublicByProduct, TradePublicByUser, Size, TradeCreate, WhatDo

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def test_trade(test_user:UserInDB, test_product:ProductInDB, db:session.Session):
    new_trade = TradeCreate(
        product_id = test_product.id,
        what_do = WhatDo.trade,
        comment = "didn't like smell",
        size = Size.travel
    )
    existing_trade = db.query(Trade).filter(
        Trade.user_id == test_user.id, 
        Trade.product_id == test_product.id,
        Trade.what_do == "trade",
        Trade.comment == "didn't like smell",
        Trade.size == "travel",
    ).first()
    if existing_trade:
        return existing_trade
    trade_repo = TradeRepository(db)
    return trade_repo.create_trade(trade_create= new_trade, user_id=test_user.id)

@pytest.fixture
async def test_trade2(test_user2:UserInDB, test_product:ProductInDB, db:session.Session):
    new_trade = TradeCreate(
        product_id = test_product.id,
        what_do = WhatDo.giveaway,
        comment = "doesn't work for me",
        size = Size.jumbo
    )
    existing_trade = db.query(Trade).filter(
        Trade.user_id == test_user2.id, 
        Trade.product_id == test_product.id,
        Trade.what_do == "give away",
        Trade.comment == "doesn't work for me",
        Trade.size == "jumbo",
    ).first()
    if existing_trade:
        return existing_trade
    trade_repo = TradeRepository(db)
    return trade_repo.create_trade(trade_create= new_trade, user_id = test_user2.id)

class TestCreateTrade:
    async def test_logged_in_users_can_create_trade(self, app: FastAPI, authorized_client: AsyncClient, test_user: UserInDB, test_product:ProductInDB) -> None:
        new_trade = TradeCreate(
            user_id = test_user.id,
            product_id = test_product.id,
            what_do = "trade",
        )
        res = await authorized_client.post(
            app.url_path_for("trades:create-trade"), json={"new_trade":new_trade.dict()}
        )
        assert res.status_code == HTTP_201_CREATED

        created_trade = TradeCreate(**res.json())
        assert created_trade == new_trade

    async def test_unauthenticated_users_cannot_create_trades(self, app: FastAPI, client: AsyncClient, test_user2: UserInDB, test_product:ProductInDB) -> None:
        new_trade = TradeCreate(
            user_id = test_user2.id,
            product_id = test_product.id,
            what_do = "trade",
        )
        res = await client.post(
            app.url_path_for("trades:create-trade"), json={"new_trade":new_trade.dict()}
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        "invalid_payload, status_code",
        (
            (None, 422),
            ({}, 422),
            ({"what_do": "trade"}, 422),
            ({"size": "jumbo", "what_do": "trade", "comment": "test"}, 422),
            ({"comment": "test", "size": "jumbo", "price": 400}, 422),
        ),
    )
    async def test_invalid_input_raises_error(
        self, app:FastAPI, authorized_client: AsyncClient, invalid_payload:dict,status_code:int
    ) -> None:
        res = await authorized_client.post(
            app.url_path_for("trades:create-trade"),json={"new_trade":invalid_payload}
        )
        assert res.status_code == status_code

class TestGetTrade:
   
    async def test_trade_can_be_retrieved_by_id(self, app:FastAPI, client: AsyncClient, test_trade:TradeInDB)-> None:
        res = await client.get(app.url_path_for("trades:get-trade-by-id", trade_id=test_trade.id))
        returned_trade = TradePublic(**res.json())
        assert TradePublic.from_orm(test_trade) == returned_trade

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
        res = await client.get(app.url_path_for("trades:get-trade-by-id", trade_id=id))
        assert res.status_code == status_code

    async def test_trades_can_be_retrieved_by_user(self, app:FastAPI, client: AsyncClient,test_trade:TradeInDB, test_user:UserInDB, test_product: ProductInDB, db:session.Session) -> None:
        nu_trade_create2 = TradeCreate(
            product_id = test_product.id,
            what_do = WhatDo.giveaway,
            size = Size.sample
        )
        trade_repo = TradeRepository(db)
        nu_trade1 = TradePublicByUser.from_orm(trade_repo.create_trade(trade_create = nu_trade_create2, user_id = test_user.id)) 
        res = await client.get(app.url_path_for("trades:get-trades-by-user", user_id = test_user.id))
        trades = [TradePublicByUser(**l) for l in res.json()] 
        assert TradePublicByUser.from_orm(test_trade) in trades
        assert nu_trade1 in trades   

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
        res = await client.get(app.url_path_for("trades:get-trades-by-user", user_id=user_id))
        assert res.status_code == status_code

    async def test_trades_can_be_retrieved_by_product(self, app:FastAPI, client: AsyncClient, test_trade:TradeInDB, test_user:UserInDB, test_product: ProductInDB, db:session.Session) -> None:
        nu_trade_create2 = TradeCreate(
            product_id = test_product.id,
            what_do = WhatDo.giveaway,
            size = Size.sample
        )
        trade_repo = TradeRepository(db)
        nu_trade1 = TradePublicByProduct.from_orm(trade_repo.create_trade(trade_create = nu_trade_create2, user_id = test_user.id)) 
        res = await client.get(app.url_path_for("trades:get-trades-by-product", product_id = test_product.id))
        trades = [TradePublicByProduct(**l) for l in res.json()] 
        assert TradePublicByProduct.from_orm(test_trade) in trades
        assert nu_trade1 in trades   

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
        res = await client.get(app.url_path_for("trades:get-trades-by-product", product_id=product_id))
        assert res.status_code == status_code

    async def test_all_trades_can_be_retrieved(self, app:FastAPI, client:AsyncClient) -> None:
        res = await client.get(app.url_path_for("trades:get-all-trades"))
        assert res.status_code == HTTP_200_OK
        assert isinstance(res.json(), list)
        assert len(res.json()) > 0

class TestUpdateTrade:
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
    async def test_update_trade_with_valid_input(
        self,
        app:FastAPI,
        authorized_client: AsyncClient,
        test_trade: Trade,
        attrs_to_change: List[str],
        values: List[str],
    ) -> None:
        trade_update = {
            "trade_update": {
                attrs_to_change[i]: values[i] for i in range(len(attrs_to_change))
            }
        }
        res = await authorized_client.put(
            app.url_path_for(
                "trades:update-trade-by-id",
                trade_id=test_trade.id,
            ),
            json = trade_update
        )
        assert res.status_code == HTTP_200_OK
        updated_trade = TradePublic(**res.json())
        assert updated_trade.id == test_trade.id  # make sure it's the same cleaning
        # make sure that any attribute we updated has changed to the correct value
        target_trade = TradePublic.from_orm(test_trade)
        print(updated_trade)
        print(target_trade)
        for i in range(len(attrs_to_change)):
            attr_to_change = getattr(updated_trade, attrs_to_change[i])
            assert attr_to_change != getattr(test_trade, attrs_to_change[i])
            assert attr_to_change == values[i] 
        # make sure that no other attributes' values have changed
        
        for attr, value in updated_trade.dict().items():
            if attr not in attrs_to_change and attr != "updated_at":
                assert getattr(target_trade, attr) == value

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
    async def test_update_trade_with_invalid_input_throws_error(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
        id: int,
        payload: dict,
        status_code: int,
    ) -> None:
        trade_update = {"trade_update": payload}
        res = await authorized_client.put(
            app.url_path_for("trades:update-trade-by-id", trade_id=id),
            json=trade_update
        )
        assert res.status_code == status_code

    async def test_trade_cannot_be_updated_if_not_logged_in(self, app:FastAPI, client: AsyncClient, test_trade:TradeInDB)-> None:
        res = await client.put(app.url_path_for("trades:update-trade-by-id", trade_id=test_trade.id), json={"trade_update": {"price": 99.99}})
        assert res.status_code == HTTP_401_UNAUTHORIZED
      
    async def test_user_cannot_update_other_users_trade(
        self,
        app:FastAPI,
        authorized_client:AsyncClient,
        test_trade2:Trade,
    ) -> None:
        res = await authorized_client.put(
            app.url_path_for("trades:update-trade-by-id", trade_id=test_trade2.id),
            json={"trade_update": {"price": 99.99}},
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN

class TestDeleteTrade:
    async def test_trade_can_be_deleted(self, app:FastAPI, authorized_client: AsyncClient, test_trade:TradeInDB)-> None:
        res = await authorized_client.delete(app.url_path_for("trades:delete-trade-by-id", trade_id=test_trade.id))
        assert res.status_code == HTTP_200_OK
        # ensure that the trade no longer exists
        res = await authorized_client.get(
            app.url_path_for(
                "trades:get-trade-by-id", 
                trade_id=test_trade.id,
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
        res = await client.get(app.url_path_for("trades:delete-trade-by-id", trade_id=id))
        assert res.status_code == status_code

    async def test_trade_cannot_be_deleted_if_not_logged_in(self, app:FastAPI, client: AsyncClient, test_trade:TradeInDB)-> None:
        res = await client.delete(app.url_path_for("trades:delete-trade-by-id", trade_id=test_trade.id))
        assert res.status_code == HTTP_401_UNAUTHORIZED

    async def test_authenticated_users_cannot_delete_trades_for_other_users(self, app: FastAPI, authorized_client: AsyncClient, test_trade2:TradeInDB) -> None:
        res = await authorized_client.delete(app.url_path_for("trades:delete-trade-by-id", trade_id=test_trade2.id))
        assert res.status_code == status.HTTP_403_FORBIDDEN
