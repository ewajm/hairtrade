from typing import List
from fastapi import APIRouter, Path, Body, Depends
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.api.dependencies.trades import check_trade_modification_permissions, get_trade_by_id_from_path
from app.db.metadata import Trade
from app.db.repositories.trades import TradeRepository
from app.models.user import UserInDB

from app.models.trade import TradeCreate, TradePublic, TradePublicByProduct, TradePublicByUser, TradeUpdate

router = APIRouter()

@router.post("/", response_model=TradePublicByUser, name="trades:create-trade", status_code=HTTP_201_CREATED)
def create_new_trade(
    new_trade: TradeCreate = Body(..., embed=True),
    current_user: UserInDB = Depends(get_current_active_user),
    trade_repo: TradeRepository = Depends(get_repository(TradeRepository)),
) -> TradePublicByUser:
    created_trade = trade_repo.create_trade(trade_create=new_trade, user_id=current_user.id)
    return TradePublicByUser.from_orm(created_trade)    

@router.get("/{trade_id}/", response_model=TradePublic, name = "trades:get-trade-by-id")
def get_trade_by_id(
    trade_id: int = Path(..., ge=1, title="The ID of the trade to retrieve."),
    trade_repo: TradeRepository = Depends(get_repository(TradeRepository))
) -> TradePublic:
    trade = trade_repo.get_trade_by_id(id=trade_id)

    if not trade:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="no trade found with that id.")

    return TradePublic.from_orm(trade)

@router.get("/users/{user_id}/", response_model=List[TradePublicByUser], name = "trades:get-trades-by-user")
def get_trade_by_id(
    user_id: int = Path(..., ge=1, title="The ID of the user to get trades for."),
    trade_repo: TradeRepository = Depends(get_repository(TradeRepository))
) -> List[TradePublicByUser]:
    trades = trade_repo.get_trades_by_user_id(user_id=user_id)

    if not trades:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="no trades found for that user.")

    return [TradePublicByUser.from_orm(l) for l in trades]

@router.get("/products/{product_id}/", response_model=List[TradePublicByProduct], name = "trades:get-trades-by-product")
def get_trade_by_id(
    product_id: int = Path(..., ge=1, title="The ID of the product to get trades for."),
    trade_repo: TradeRepository = Depends(get_repository(TradeRepository))
) -> List[TradePublicByProduct]:
    trades = trade_repo.get_trades_by_product_id(product_id=product_id)

    if not trades:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="no trades found for that product.")

    return [TradePublicByProduct.from_orm(l) for l in trades]

@router.get("/", response_model=List[TradePublic], name="trades:get-all-trades")
def get_all_trades(
    trade_repo: TradeRepository = Depends(get_repository(TradeRepository)),
) -> List[TradePublic]:
    all_trades = trade_repo.get_all_trades()
    return [TradePublic.from_orm(l) for l in all_trades]

@router.put(
    "/{trade_id}/", 
    response_model=TradePublic, 
    name="trades:update-trade-by-id",
    dependencies=[Depends(check_trade_modification_permissions)],
    )
def update_trade_by_id(
    trade: Trade = Depends(get_trade_by_id_from_path),
    trade_update: TradeUpdate=Body(..., embed=True),
    trade_repo: TradeRepository = Depends(get_repository(TradeRepository))
) -> TradePublic:
    return TradePublic.from_orm(trade_repo.update_trade(trade=trade, trade_update=trade_update))


@router.delete(
    "/{trade_id}/", 
    response_model=int, 
    name="trades:delete-trade-by-id",
    dependencies=[Depends(check_trade_modification_permissions)],
    )
def delete_trade_by_id(
    trade: Trade = Depends(get_trade_by_id_from_path),
    trade_repo: TradeRepository = Depends(get_repository(TradeRepository)),
):
    deleted_id = trade_repo.delete_trade_by_id(trade=trade)
    return deleted_id


