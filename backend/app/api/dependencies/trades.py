from fastapi import HTTPException, Depends, Path, status
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user
from app.db.metadata import Trade
from app.models.user import UserInDB
from app.db.repositories.trades import TradeRepository

def get_trade_by_id_from_path(
    trade_id: int = Path(..., ge=1),
    trade_repo: TradeRepository = Depends(get_repository(TradeRepository)),
) -> Trade:
    trade = trade_repo.get_trade_by_id(id=trade_id)
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No trade found with that id.",
        )
    return trade


def check_trade_modification_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    trade: Trade = Depends(get_trade_by_id_from_path),
) -> None:
    if trade.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Action forbidden. Users are only able to modify trades they own.",
        )