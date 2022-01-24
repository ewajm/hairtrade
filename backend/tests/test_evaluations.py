from typing import List, Callable

import pytest

from httpx import AsyncClient
from fastapi import FastAPI, status

from app.models.trade import TradeInDB
from app.models.user import UserInDB
from app.models.offer import OfferInDB
from app.models.evaluation import EvaluationCreate, EvaluationInDB, EvaluationPublic, EvaluationAggregate


pytestmark = pytest.mark.asyncio


class TestEvaluationRoutes:
    async def test_routes_exist(self, app: FastAPI, client: AsyncClient, test_trade:TradeInDB, test_user2: UserInDB) -> None:
        res = await client.post(
            app.url_path_for("evaluations:create-evaluation-for-trade", trade_id=test_trade.id, username=test_user2.username)
        )
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.get(
            app.url_path_for("evaluations:get-evaluation-for-user", trade_id=test_trade.id, username=test_user2.username)
        )
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.get(app.url_path_for("evaluations:list-evaluations-for-user", username=test_user2.username))
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.get(app.url_path_for("evaluations:get-stats-for-user", username=test_user2.username))
        assert res.status_code != status.HTTP_404_NOT_FOUND

class TestCreateEvaluations:

    async def test_recipient_can_leave_evaluation_for_trader_and_mark_offer_completed(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user2: UserInDB,
        test_user3: UserInDB,
        test_trade_with_accepted_offer: TradeInDB,
    ) -> None:
        evaluation_create = EvaluationCreate(
            no_show=False,
            responsiveness=5,
            demeanor=5,
            overall_rating=5,
        )
        authorized_client = create_authorized_client(user=test_user3)
        res = await authorized_client.post(
            app.url_path_for(
                "evaluations:create-evaluation-for-trade",
                trade_id=test_trade_with_accepted_offer.id,
                username=test_user2.username,
            ),
            json={"evaluation_create": evaluation_create.dict()},
        )
        assert res.status_code == status.HTTP_201_CREATED
        evaluation = EvaluationInDB(**res.json())
        assert evaluation.no_show == evaluation_create.no_show
        assert evaluation.overall_rating == evaluation_create.overall_rating
        # check that the offer has now been marked as "completed"
        res = await authorized_client.get(
            app.url_path_for(
                "offers:get-offer-from-user",
                trade_id=test_trade_with_accepted_offer.id,
                username=test_user3.username,
            )
        )
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["status"] == "completed"

    async def test_non_recipient_cant_leave_review(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user4: UserInDB,
        test_user2: UserInDB,
        test_trade_with_accepted_offer: TradeInDB,
    ) -> None:
        authorized_client = create_authorized_client(user=test_user4)
        res = await authorized_client.post(
            app.url_path_for(
                "evaluations:create-evaluation-for-trade",
                trade_id=test_trade_with_accepted_offer.id,
                username=test_user2.username,
            ),
            json={"evaluation_create": {"overall_rating": 2}},
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN

    async def test_cant_leave_multiple_reviews(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user2: UserInDB,
        test_user3: UserInDB,
        test_trade_with_accepted_offer: TradeInDB,
    ) -> None:
        authorized_client = create_authorized_client(user=test_user3)
        res = await authorized_client.post(
            app.url_path_for(
                "evaluations:create-evaluation-for-trade",
                trade_id=test_trade_with_accepted_offer.id,
                username=test_user2.username,
            ),
            json={"evaluation_create": {"overall_rating": 3}},
        )
        assert res.status_code == status.HTTP_201_CREATED
        res = await authorized_client.post(
            app.url_path_for(
                "evaluations:create-evaluation-for-trade",
                trade_id=test_trade_with_accepted_offer.id,
                username=test_user2.username,
            ),
            json={"evaluation_create": {"overall_rating": 1}},
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST