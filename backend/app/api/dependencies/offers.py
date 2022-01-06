from fastapi import HTTPException, Depends, status

from app.models.user import UserInDB
from app.models.item import ItemInDB
from app.db.repositories.offers import OffersRepository

from app.api.dependencies.database import get_repository
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.items import get_item_by_id_from_path


async def check_offer_create_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
    item: ItemInDB = Depends(get_item_by_id_from_path),
    offers_repo: OffersRepository = Depends(get_repository(OffersRepository)),
) -> None:
    if item.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users are unable to create offers for items they own.",
        )

