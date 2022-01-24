from typing import List

from fastapi import HTTPException, Depends, Path, status
from app.models.trade import TradeInDB

from app.models.user import UserInDB
from app.models.offer import OfferInDB, OfferStatus
from app.models.evaluation import EvaluationInDB

from app.db.repositories.evaluations import EvaluationsRepository

from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.users import get_user_by_username_from_path
from app.api.dependencies.trades import get_trade_by_id_from_path
from app.api.dependencies.offers import get_offer_for_trade_from_current_user


async def check_evaluation_create_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    trade: TradeInDB = Depends(get_trade_by_id_from_path),
    trader: UserInDB = Depends(get_user_by_username_from_path),
    offer: OfferInDB = Depends(get_offer_for_trade_from_current_user),
    evals_repo: EvaluationsRepository = Depends(get_repository(EvaluationsRepository)),
) -> None:
    if offer.status == OfferStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A review has already been completed for this trade.",
        )
    # Check that evaluations can only be made for jobs that have been accepted
    # Also serves to ensure that only one evaluation per-cleaner-per-job is allowed
    if offer.status != OfferStatus.accepted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only users with accepted offers can leave evaluations.",
        )
    # Check that evaluations can only be made for users 
    if trade.user_id != trader.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot leave an evaluation for an unrelated user.",
        )

