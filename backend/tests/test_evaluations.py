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
    async def test_routes_exist(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(
            app.url_path_for("evaluations:create-evaluation-for-trade", trade_id=1, username="bradpitt")
        )
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.get(
            app.url_path_for("evaluations:get-evaluation-for-user", trade_id=1, username="bradpitt")
        )
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.get(app.url_path_for("evaluations:list-evaluations-for-user", username="bradpitt"))
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.get(app.url_path_for("evaluations:get-stats-for-user", username="bradpitt"))
        assert res.status_code != status.HTTP_404_NOT_FOUND

