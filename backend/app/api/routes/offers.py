from typing import List

from fastapi import APIRouter, Path, Body, status, Depends
from fastapi.exceptions import HTTPException
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.api.dependencies.trades import get_trade_by_id_from_path
from app.api.dependencies.offers import check_offer_create_permissions, check_offer_rescind_permissions, get_offer_for_trade_from_current_user
from app.db.metadata import Offer, Trade
from app.db.repositories.offers import OffersRepository
from app.models.trade import TradeInDB

from app.models.offer import OfferCreate, OfferUpdate, OfferInDB, OfferPublic
from app.models.user import UserInDB


router = APIRouter()

from app.api.dependencies.offers import (
    check_offer_create_permissions,
    check_offer_get_permissions,
    check_offer_list_permissions,
    check_offer_acceptance_permissions,
    check_offer_cancel_permissions,
    get_offer_for_trade_from_user_by_path,
    list_offers_for_trade_by_id_from_path,
)


@router.post(
    "/", 
    response_model=OfferPublic, 
    name="offers:create-offer", 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_offer_create_permissions)],)
async def create_offer(
    trade: Trade = Depends(get_trade_by_id_from_path),
    current_user: UserInDB = Depends(get_current_active_user),
    offers_repo: OffersRepository = Depends(get_repository(OffersRepository)),
) -> OfferPublic:
    new_offer = OfferCreate(trade_id=trade.id, user_id=current_user.id)
    return OfferPublic.from_orm(offers_repo.create_offer_for_trade(new_offer=new_offer))





@router.get(
    "/",
    response_model=List[OfferPublic],
    name="offers:list-offers-for-trade",
    dependencies=[Depends(check_offer_list_permissions)],
)
def list_offers_for_trade(
    offers: List[OfferInDB] = Depends(list_offers_for_trade_by_id_from_path)
) -> List[OfferPublic]:
    return [OfferPublic.from_orm(l) for l in offers]




@router.get(
    "/{username}/",
    response_model=OfferPublic,
    name="offers:get-offer-from-user",
    dependencies=[Depends(check_offer_get_permissions)],
)
def get_offer_from_user(offer: OfferInDB = Depends(get_offer_for_trade_from_user_by_path)) -> OfferPublic:
    return OfferPublic.from_orm(offer)




@router.put(
    "/{username}/",
    response_model=OfferPublic,
    name="offers:accept-offer-from-user",
    dependencies=[Depends(check_offer_acceptance_permissions)],
)
async def accept_offer(
    offer: Offer = Depends(get_offer_for_trade_from_user_by_path),
    offers_repo: OffersRepository = Depends(get_repository(OffersRepository)),
) -> OfferPublic:
    return OfferPublic.from_orm(offers_repo.accept_offer(offer=offer, offer_update=OfferUpdate(status="accepted")))




@router.put(
    "/",
    response_model=OfferPublic,
    name="offers:cancel-offer-from-user",
    dependencies=[Depends(check_offer_cancel_permissions)],
)
async def cancel_offer(
    offer: OfferInDB = Depends(get_offer_for_trade_from_current_user),
    offers_repo: OffersRepository = Depends(get_repository(OffersRepository)),
) -> OfferPublic:
    return OfferPublic.from_orm(offers_repo.cancel_offer(offer=offer, offer_update=OfferUpdate(status="cancelled"))) 



@router.delete(
    "/",
    response_model=OfferPublic,
    name="offers:rescind-offer-from-user",
    dependencies=[Depends(check_offer_rescind_permissions)],
)
async def rescind_offer(
    offer: OfferInDB = Depends(get_offer_for_trade_from_current_user),
    offers_repo: OffersRepository = Depends(get_repository(OffersRepository)),
) -> OfferPublic:
    return OfferPublic.from_orm(offers_repo.rescind_offer(offer=offer))