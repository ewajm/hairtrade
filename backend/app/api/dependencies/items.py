from fastapi import HTTPException, Depends, Path, status
from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user
from app.db.metadata import Item
from app.models.item import ItemInDB
from app.models.user import UserInDB
from app.db.repositories.items import ItemRepository

def get_item_by_id_from_path(
    id: int = Path(..., ge=1),
    item_repo: ItemRepository = Depends(get_repository(ItemRepository)),
) -> Item:
    item = item_repo.get_item_by_id(id=id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No item found with that id.",
        )
    return item


def check_item_modification_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    item: Item = Depends(get_item_by_id_from_path),
) -> None:
    if item.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Action forbidden. Users are only able to modify items they own.",
        )