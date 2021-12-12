from fastapi import APIRouter, Path, Body, Depends, status
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_201_CREATED
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.db.repositories.items import ItemRepository
from app.models.user import UserInDB

from app.models.item import ItemCreate, ItemPublicByUser

router = APIRouter()

@router.post("/", response_model=ItemPublicByUser, name="items:create-item", status_code=HTTP_201_CREATED)
def create_new_item(
    new_item: ItemCreate = Body(..., embed=True),
    # current_user: UserInDB = Depends(get_current_active_user),
    item_repo: ItemRepository = Depends(get_repository(ItemRepository)),
) -> ItemPublicByUser:
    # if current_user.id != new_item.user_id:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cannot create products for other users")
    created_item = item_repo.create_item(item_create=new_item)
    return ItemPublicByUser.from_orm(created_item)    

