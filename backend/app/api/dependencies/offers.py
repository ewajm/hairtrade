from typing import List
from fastapi import HTTPException, Depends, status
from app.api.dependencies.users import get_user_by_username_from_path
from app.models.offer import OfferInDB

from app.models.user import UserInDB
from app.models.item import ItemInDB
from app.db.repositories.offers import OffersRepository

from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.items import get_item_by_id_from_path


def get_offer_for_item_from_user(
    *, user: UserInDB, item: ItemInDB, offers_repo: OffersRepository,
) -> OfferInDB:
    offer = offers_repo.get_offer_for_item_from_user(item=item, user=user)
    if not offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found.")
    return offer

def get_offer_for_item_from_user_by_path(
    user: UserInDB = Depends(get_user_by_username_from_path),
    item: ItemInDB = Depends(get_item_by_id_from_path),
    offers_repo: OffersRepository = Depends(get_repository(OffersRepository)),
) -> OfferInDB:
    return get_offer_for_item_from_user(user=user, item=item, offers_repo=offers_repo)

def list_offers_for_item_by_id_from_path(
    item: ItemInDB = Depends(get_item_by_id_from_path),
    offers_repo: OffersRepository = Depends(get_repository(OffersRepository)),
) -> List[OfferInDB]:
    return offers_repo.list_offers_for_item(item=item)

def check_offer_create_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    item: ItemInDB = Depends(get_item_by_id_from_path),
    offers_repo: OffersRepository = Depends(get_repository(OffersRepository)),
) -> None:
    if item.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users are unable to create offers for items they own.",
        )
    if offers_repo.get_offer_for_item_from_user(item=item, user=current_user):
        print("Users aren't allowed create more than one offer for an item.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users aren't allowed create more than one offer for an item.",
        )

def check_offer_list_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    item: ItemInDB = Depends(get_item_by_id_from_path),
) -> None:
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unable to access offers.",
        )

def check_offer_get_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    item: ItemInDB = Depends(get_item_by_id_from_path),
    offer: OfferInDB = Depends(get_offer_for_item_from_user_by_path),
) -> None:
    if item.user_id != current_user.id and offer.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unable to access offer.",
        )        
