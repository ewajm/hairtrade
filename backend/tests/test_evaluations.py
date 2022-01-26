from statistics import mean
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
            app.url_path_for("evaluations:get-evaluation-for-trade", trade_id=test_trade.id, username=test_user2.username)
        )
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.get(app.url_path_for("evaluations:list-evaluations-for-trader", username=test_user2.username))
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.get(app.url_path_for("evaluations:get-stats-for-trader", username=test_user2.username))
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

class TestGetEvaluations:
    """
    Test that authenticated user who is not owner or recipient can fetch a single evaluation
    Test that authenticated user can fetch all of a trader's evaluations
    Test that a trader's evaluations comes with an aggregate
    """
    async def test_authenticated_user_can_get_evaluation_for_trade(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user2: UserInDB,
        test_user4: UserInDB,
        test_list_of_trades_with_evaluated_offer: List[TradeInDB],
    ) -> None:
        authorized_client = create_authorized_client(user=test_user4)
        res = await authorized_client.get(
            app.url_path_for(
                "evaluations:get-evaluation-for-trade",
                trade_id=test_list_of_trades_with_evaluated_offer[0].id,
                username=test_user2.username,
            )
        )
        assert res.status_code == status.HTTP_200_OK
        evaluation = EvaluationPublic(**res.json())
        assert evaluation.trade_id == test_list_of_trades_with_evaluated_offer[0].id
        assert evaluation.trader_id == test_user2.id
        assert evaluation.responsiveness >= 0 and evaluation.responsiveness <= 5
        assert evaluation.demeanor >= 0 and evaluation.demeanor <= 5
        assert evaluation.overall_rating >= 0 and evaluation.overall_rating <= 5

    async def test_authenticated_user_can_get_list_of_evaluations_for_cleaner(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user2: UserInDB,
        test_user4: UserInDB,
        test_list_of_trades_with_evaluated_offer: List[TradeInDB],
    ) -> None:
        authorized_client = create_authorized_client(user=test_user4)
        res = await authorized_client.get(
            app.url_path_for("evaluations:list-evaluations-for-trader", username=test_user2.username)
        )
        assert res.status_code == status.HTTP_200_OK
        evaluations = [EvaluationPublic(**e) for e in res.json()]
        assert len(evaluations) > 1
        for evaluation in evaluations:
            assert evaluation.trader_id == test_user2.id
            assert evaluation.overall_rating >= 0

    async def test_authenticated_user_can_get_aggregate_stats_for_cleaner(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user2: UserInDB,
        test_user4: UserInDB,
        test_list_of_trades_with_evaluated_offer: List[TradeInDB],
    ) -> None:
        authorized_client = create_authorized_client(user=test_user4)
        res = await authorized_client.get(
            app.url_path_for("evaluations:list-evaluations-for-trader", username=test_user2.username)
        )
        assert res.status_code == status.HTTP_200_OK
        evaluations = [EvaluationPublic(**e) for e in res.json()]
        res = await authorized_client.get(
            app.url_path_for("evaluations:get-stats-for-trader", username=test_user2.username)
        )
        assert res.status_code == status.HTTP_200_OK
        stats = EvaluationAggregate(**res.json())
        assert len(evaluations) == stats.total_evaluations
        assert max([e.overall_rating for e in evaluations]) == stats.max_overall_rating
        assert min([e.overall_rating for e in evaluations]) == stats.min_overall_rating
        assert mean([e.overall_rating for e in evaluations]) == stats.avg_overall_rating
        assert (
            mean([e.responsiveness for e in evaluations if e.responsiveness is not None]) == stats.avg_responsiveness
        )
        assert mean([e.demeanor for e in evaluations if e.demeanor is not None]) == stats.avg_demeanor
        assert len([e for e in evaluations if e.overall_rating == 1]) == stats.one_stars
        assert len([e for e in evaluations if e.overall_rating == 2]) == stats.two_stars
        assert len([e for e in evaluations if e.overall_rating == 3]) == stats.three_stars
        assert len([e for e in evaluations if e.overall_rating == 4]) == stats.four_stars
        assert len([e for e in evaluations if e.overall_rating == 5]) == stats.five_stars

    async def test_unauthenticated_user_forbidden_from_get_requests(
        self,
        app: FastAPI,
        client: AsyncClient,
        test_user2: UserInDB,
        test_list_of_trades_with_evaluated_offer: List[TradeInDB],
    ) -> None:
        res = await client.get(
            app.url_path_for(
                "evaluations:get-evaluation-for-trade",
                trade_id=test_list_of_trades_with_evaluated_offer[0].id,
                username=test_user2.username,
            )
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
        res = await client.get(
            app.url_path_for("evaluations:list-evaluations-for-trader", username=test_user2.username)
        )
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
