from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path
from pydantic.tools import parse_obj_as
from sqlalchemy.orm import session
from sqlalchemy.sql.expression import delete
from sqlalchemy.sql.sqltypes import Integer
from starlette.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND
from app.api.dependencies.auth import get_current_active_user
from app.models.product import ProductCreate, ProductPublic  
from app.db.repositories.products import ProductsRepository  
from app.api.dependencies.database import get_repository
from app.models.product import ProductUpdate
from app.models.user import UserInDB

router = APIRouter()

@router.get("/", response_model=List[ProductPublic], name="products:get-all-products")
def get_all_products(
    product_repo: ProductsRepository = Depends(get_repository(ProductsRepository)),
) -> List[ProductPublic]:
    all_products = product_repo.get_all_products()
    return [ProductPublic.from_orm(l) for l in all_products]

@router.get("/{id}/", response_model=ProductPublic, name="products:get-product-by-id")
def get_product_by_id(
    id:int,
    product_repo: ProductsRepository = Depends(get_repository(ProductsRepository)),
) -> ProductPublic:
    product = product_repo.get_product_by_id(id=id)

    if not product:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="no product found with that id.")

    return ProductPublic.from_orm(product)

@router.post("/", response_model=ProductPublic, name="products:create-product", status_code=HTTP_201_CREATED)
def create_new_product(
    new_product: ProductCreate = Body(..., embed=True),
    current_user: UserInDB = Depends(get_current_active_user),
    products_repo: ProductsRepository = Depends(get_repository(ProductsRepository)),
) -> ProductPublic:
    created_product = products_repo.create_product(new_product=new_product)
    return ProductPublic.from_orm(created_product)

@router.put("/{id}/", response_model=ProductPublic, name="products:update-product-by-id")
def update_product(
    id:int = Path(..., ge=1, title="The ID of the product to update."),
    current_user: UserInDB = Depends(get_current_active_user),
    product_update: ProductUpdate=Body(..., embed=True),
    products_repo: ProductsRepository = Depends(get_repository(ProductsRepository)),
) -> ProductPublic:
    updated_product = products_repo.update_product(id=id, product_update=product_update)
    if not updated_product:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="no product found with that id.")

    return ProductPublic.from_orm(updated_product)


@router.delete("/{id}/", response_model=int, name = "products:delete-product-by-id")
def delete_product_by_id(
    id: int = Path(..., ge=1, title="The ID of the cleaning to delete."),
    current_user: UserInDB = Depends(get_current_active_user),
    product_repo: ProductsRepository = Depends(get_repository(ProductsRepository)),
) -> int:
    deleted_id = product_repo.delete_product_by_id(id=id)

    if not deleted_id:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="no product found with that id.")

    return deleted_id