from typing import List
from fastapi import APIRouter, Path, Body, Depends, status
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.db.repositories.items import ItemRepository
from app.models.user import UserInDB

from app.models.item import ItemCreate, ItemPublic, ItemPublicByUser

router = APIRouter()

@router.post("/", response_model=ItemPublicByUser, name="items:create-item", status_code=HTTP_201_CREATED)
def create_new_item(
    new_item: ItemCreate = Body(..., embed=True),
    current_user: UserInDB = Depends(get_current_active_user),
    item_repo: ItemRepository = Depends(get_repository(ItemRepository)),
) -> ItemPublicByUser:
    if current_user.id != new_item.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cannot create products for other users")
    created_item = item_repo.create_item(item_create=new_item)
    return ItemPublicByUser.from_orm(created_item)    

@router.get("/{id}/", response_model=ItemPublic, name = "items:get-item-by-id")
def get_item_by_id(
    id: int = Path(..., ge=1, title="The ID of the item to retrieve."),
    item_repo: ItemRepository = Depends(get_repository(ItemRepository))
) -> ItemPublic:
    item = item_repo.get_item_by_id(id=id)

    if not item:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="no item found with that id.")

    return ItemPublic.from_orm(item)

@router.get("/users/{user_id}/", response_model=List[ItemPublicByUser], name = "items:get-items-by-user")
def get_item_by_id(
    user_id: int = Path(..., ge=1, title="The ID of the user to get items for."),
    item_repo: ItemRepository = Depends(get_repository(ItemRepository))
) -> List[ItemPublicByUser]:
    items = item_repo.get_items_by_user_id(user_id=user_id)

    if not items:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="no items found for that user.")

    return [ItemPublicByUser.from_orm(l) for l in items]