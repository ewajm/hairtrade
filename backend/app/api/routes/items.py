from typing import List
from fastapi import APIRouter, Path, Body, Depends, status
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.db.repositories.items import ItemRepository
from app.models.user import UserInDB

from app.models.item import ItemCreate, ItemPublic, ItemPublicByProduct, ItemPublicByUser, ItemUpdate

router = APIRouter()

@router.post("/", response_model=ItemPublicByUser, name="items:create-item", status_code=HTTP_201_CREATED)
def create_new_item(
    new_item: ItemCreate = Body(..., embed=True),
    current_user: UserInDB = Depends(get_current_active_user),
    item_repo: ItemRepository = Depends(get_repository(ItemRepository)),
) -> ItemPublicByUser:
    created_item = item_repo.create_item(item_create=new_item, user_id=current_user.id)
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

@router.get("/products/{product_id}/", response_model=List[ItemPublicByProduct], name = "items:get-items-by-product")
def get_item_by_id(
    product_id: int = Path(..., ge=1, title="The ID of the product to get items for."),
    item_repo: ItemRepository = Depends(get_repository(ItemRepository))
) -> List[ItemPublicByProduct]:
    items = item_repo.get_items_by_product_id(product_id=product_id)

    if not items:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="no items found for that product.")

    return [ItemPublicByProduct.from_orm(l) for l in items]

@router.get("/", response_model=List[ItemPublic], name="items:get-all-items")
def get_all_products(
    item_repo: ItemRepository = Depends(get_repository(ItemRepository)),
) -> List[ItemPublic]:
    all_items = item_repo.get_all_items()
    return [ItemPublic.from_orm(l) for l in all_items]

@router.put("/{id}/", response_model=ItemPublic, name="items:update-item-by-id")
def update_item_by_id(
    id: int = Path(..., ge=1, title="The ID of the item to retrieve."),
    item_update: ItemUpdate=Body(..., embed=True),
    current_user: UserInDB = Depends(get_current_active_user),
    item_repo: ItemRepository = Depends(get_repository(ItemRepository))
) -> ItemPublic:
   
    updated_item = item_repo.update_item(id=id, item_update=item_update, requesting_user_id=current_user.id)
    if not updated_item:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="no item found with that id.")

    return ItemPublic.from_orm(updated_item)


@router.delete("/{id}/", response_model=int, name="items:delete-item-by-id")
def delete_item_by_id(
    id: int = Path(..., ge=1, title="The ID of the item to delete."),
    current_user: UserInDB = Depends(get_current_active_user),
    item_repo: ItemRepository = Depends(get_repository(ItemRepository)),
):
    deleted_id = item_repo.delete_item_by_id(id=id, requesting_user_id=current_user.id)
    return deleted_id


