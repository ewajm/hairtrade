from typing import List
from fastapi import HTTPException, Depends, status
from app.api.dependencies.users import get_user_by_username_from_path
from app.db.metadata import Offer
from app.models.offer import OfferInDB

from app.models.user import UserInDB
from app.models.trade import TradeInDB
from app.db.repositories.offers import OffersRepository

from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.trades import get_trade_by_id_from_path


def get_offer_for_trade_from_user(
    *, user: UserInDB, trade: TradeInDB, offers_repo: OffersRepository,
) -> Offer:
    offer = offers_repo.get_offer_for_trade_from_user(trade=trade, user=user)
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found.")
    return offer

def get_offer_for_trade_from_user_by_path(
    user: UserInDB = Depends(get_user_by_username_from_path),
    trade: TradeInDB = Depends(get_trade_by_id_from_path),
    offers_repo: OffersRepository = Depends(get_repository(OffersRepository)),
) -> Offer:
    return get_offer_for_trade_from_user(user=user, trade=trade, offers_repo=offers_repo)

async def get_offer_for_trade_from_current_user(
    current_user: UserInDB = Depends(get_current_active_user),
    trade: TradeInDB = Depends(get_trade_by_id_from_path),
    offers_repo: OffersRepository = Depends(get_repository(OffersRepository)),
) -> Offer:
    return get_offer_for_trade_from_user(user=current_user, trade=trade, offers_repo=offers_repo)


def list_offers_for_trade_by_id_from_path(
    trade: TradeInDB = Depends(get_trade_by_id_from_path),
    offers_repo: OffersRepository = Depends(get_repository(OffersRepository)),
) -> List[Offer]:
    return offers_repo.list_offers_for_trade(trade=trade)

def check_offer_create_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    trade: TradeInDB = Depends(get_trade_by_id_from_path),
    offers_repo: OffersRepository = Depends(get_repository(OffersRepository)),
) -> None:
    if trade.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users are unable to create offers for products for trade they own.",
        )
    if offers_repo.get_offer_for_trade_from_user(trade=trade, user=current_user):
        print("Users aren't allowed create more than one offer for a product for trade.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users aren't allowed create more than one offer for a product for trade.",
        )

def check_offer_list_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    trade: TradeInDB = Depends(get_trade_by_id_from_path),
) -> None:
    if trade.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unable to access offers.",
        )

def check_offer_get_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    trade: TradeInDB = Depends(get_trade_by_id_from_path),
    offer: OfferInDB = Depends(get_offer_for_trade_from_user_by_path),
) -> None:
    if trade.user_id != current_user.id and offer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unable to access offer.",
        )        

def check_offer_acceptance_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    trade: TradeInDB = Depends(get_trade_by_id_from_path),
    offer: OfferInDB = Depends(get_offer_for_trade_from_user_by_path),
    existing_offers: List[OfferInDB] = Depends(list_offers_for_trade_by_id_from_path)
) -> None:
    if trade.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner of the product for trade may accept offers."
        )
    if offer.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Can only accept offers that are currently pending."
        )
    if "accepted" in [o.status for o in existing_offers]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="That product for trade already has an accepted offer."
        )

def check_offer_cancel_permissions(offer: OfferInDB = Depends(get_offer_for_trade_from_current_user)) -> None:
    if offer.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Can only cancel offers that have been accepted.",
        )

def check_offer_rescind_permissions(offer: OfferInDB = Depends(get_offer_for_trade_from_current_user)) -> None:
    if offer.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Can only rescind currently pending offers."
        )