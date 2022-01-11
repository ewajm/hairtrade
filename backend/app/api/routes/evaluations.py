from typing import List

from fastapi import APIRouter, Depends, Body, Path, status

from app.models.evaluation import EvaluationCreate, EvaluationInDB, EvaluationPublic, EvaluationAggregate
from app.models.user import UserInDB
from app.models.trade import TradeInDB
from app.models.offer import OfferInDB

from app.db.repositories.evaluations import EvaluationsRepository

from app.api.dependencies.database import get_repository
from app.api.dependencies.trades import get_trade_by_id_from_path
from app.api.dependencies.users import get_user_by_username_from_path


router = APIRouter()

@router.post(
    "/{trade_id}/",
    response_model=EvaluationPublic,
    name="evaluations:create-evaluation-for-trade",
    status_code=status.HTTP_201_CREATED,
)
async def create_evaluation_for_cleaner(
    evaluation_create: EvaluationCreate = Body(..., embed=True),
) -> EvaluationPublic:
    return None

@router.get(
    "/",
    response_model=List[EvaluationPublic],
    name="evaluations:list-evaluations-for-user",
)
async def list_evaluations_for_user() -> List[EvaluationPublic]:
    return None

@router.get(
    "/stats/", response_model=EvaluationAggregate, name="evaluations:get-stats-for-user",
)
async def get_stats_for_user() -> EvaluationAggregate:
    return None 

@router.get(
    "/{trade_id}/",
    response_model=EvaluationPublic,
    name="evaluations:get-evaluation-for-user",
)
async def get_evaluation_for_user() -> EvaluationPublic:
    return None

