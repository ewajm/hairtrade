from typing import List

from fastapi import APIRouter, Depends, Body, Path, status
from app.api.dependencies.evaluations import check_evaluation_create_permissions, get_trader_evaluation_for_trade_from_path, list_evaluations_for_trader_from_path
from app.api.routes.users import get_currently_authenticated_user

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
    dependencies=[Depends(check_evaluation_create_permissions)]
)
def create_evaluation_for_trade(
    evaluation_create: EvaluationCreate = Body(..., embed=True),
    trade: TradeInDB = Depends(get_trade_by_id_from_path),
    trader: UserInDB = Depends(get_user_by_username_from_path),
    reviewer: UserInDB = Depends(get_currently_authenticated_user),
    evals_repo: EvaluationsRepository = Depends(get_repository(EvaluationsRepository)),    
) -> EvaluationPublic:
    return EvaluationPublic.from_orm(evals_repo.create_evaluation_for_trade(
        evaluation_create=evaluation_create, trader=trader, trade=trade, reviewer = reviewer
    ))

@router.get(
    "/",
    response_model=List[EvaluationPublic],
    name="evaluations:list-evaluations-for-trader",
)
def list_evaluations_for_trader(
    evaluations: List[EvaluationInDB] = Depends(list_evaluations_for_trader_from_path)
) -> List[EvaluationPublic]:
    return [EvaluationPublic.from_orm(e) for e in evaluations]

@router.get(
    "/stats/", response_model=EvaluationAggregate, name="evaluations:get-stats-for-trader",
)
def get_stats_for_trader(
    trader: UserInDB = Depends(get_user_by_username_from_path),
    evals_repo: EvaluationsRepository = Depends(get_repository(EvaluationsRepository)),
) -> EvaluationAggregate:
    return EvaluationAggregate(**evals_repo.get_trader_aggregates(trader=trader))

@router.get(
    "/{trade_id}/",
    response_model=EvaluationPublic,
    name="evaluations:get-evaluation-for-trade",
)
def get_evaluation_for_trade(   
    evaluation: EvaluationInDB = Depends(get_trader_evaluation_for_trade_from_path),
) -> EvaluationPublic:
    return EvaluationPublic.from_orm(evaluation)

