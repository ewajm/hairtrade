from typing import List

from fastapi import APIRouter, Path, Body, status, Depends
from fastapi.exceptions import HTTPException
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.api.dependencies.items import get_item_by_id_from_path
from app.api.dependencies.offers import check_offer_create_permissions
from app.db.metadata import Item
from app.db.repositories.offers import OffersRepository
from app.models.item import ItemInDB

from app.models.offer import OfferCreate, OfferUpdate, OfferInDB, OfferPublic
from app.models.user import UserInDB


router = APIRouter()

from app.api.dependencies.offers import (
    check_offer_create_permissions,
    check_offer_get_permissions,
    check_offer_list_permissions,
    get_offer_for_item_from_user_by_path,
    list_offers_for_item_by_id_from_path,
)


@router.post(
    "/", 
    response_model=OfferPublic, 
    name="offers:create-offer", 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_offer_create_permissions)],)
async def create_offer(
    item: Item = Depends(get_item_by_id_from_path),
    current_user: UserInDB = Depends(get_current_active_user),
    offers_repo: OffersRepository = Depends(get_repository(OffersRepository)),
) -> OfferPublic:
    new_offer = OfferCreate(item_id=item.id, user_id=current_user.id)
    return OfferPublic.from_orm(offers_repo.create_offer_for_item(new_offer=new_offer))





@router.get(
    "/",
    response_model=List[OfferPublic],
    name="offers:list-offers-for-item",
    dependencies=[Depends(check_offer_list_permissions)],
)
def list_offers_for_cleaning(
    offers: List[OfferInDB] = Depends(list_offers_for_item_by_id_from_path)
) -> List[OfferPublic]:
    return offers




@router.get(
    "/{username}/",
    response_model=OfferPublic,
    name="offers:get-offer-from-user",
    dependencies=[Depends(check_offer_get_permissions)],
)
def get_offer_from_user(offer: OfferInDB = Depends(get_offer_for_item_from_user_by_path)) -> OfferPublic:
    return offer




@router.put("/{username}/", response_model=OfferPublic, name="offers:accept-offer-from-user")
async def accept_offer_from_user(username: str = Path(..., min_length=3)) -> OfferPublic:
    return None




@router.put("/", response_model=OfferPublic, name="offers:cancel-offer-from-user")
async def cancel_offer_from_user() -> OfferPublic:
    return None    




@router.delete("/", response_model=int, name="offers:rescind-offer-from-user")
async def rescind_offer_from_user() -> OfferPublic:
    return None

