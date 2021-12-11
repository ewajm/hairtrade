from fastapi import APIRouter, Path, Body, Depends, status
from fastapi.exceptions import HTTPException
from starlette.status import HTTP_201_CREATED
from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.db.repositories.user_products import UserProductRepository
from app.models.user import UserInDB

from app.models.user_product import UserProductCreate, UserProductPublic

router = APIRouter()

@router.post("/", response_model=UserProductPublic, name="user_products:create-user-product", status_code=HTTP_201_CREATED)
def create_new_user_product(
    new_user_product: UserProductCreate = Body(..., embed=True),
    # current_user: UserInDB = Depends(get_current_active_user),
    user_product_repo: UserProductRepository = Depends(get_repository(UserProductRepository)),
) -> UserProductPublic:
    # if current_user.id != new_user_product.user_id:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cannot create products for other users")
    created_user_product = user_product_repo.create_user_product(user_product_create=new_user_product)
    return UserProductPublic.from_orm(created_user_product)    

