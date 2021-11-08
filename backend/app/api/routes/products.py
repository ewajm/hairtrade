from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND
from app.models.product import ProductCreate, ProductPublic  
from app.db.repositories.products import ProductsRepository  
from app.api.dependencies.database import get_repository  

router = APIRouter()

@router.get("/")
def get_all_products() -> List[dict]:
    products = [
        {"id":1, "name": "Carol's Daughter Curl Refresher Spray", "product_type": "Spray", "what_do":"trade"},
        {"id":1, "name": "Ouidad Smoothing Creme", "product_type": "creme", "what_do":"giveaway"}
    ]

    return products

@router.get("/{id}/", response_model=ProductPublic, name="products:get-product-by-id")
async def get_product_by_id(
    id:int,
    product_repo: ProductsRepository = Depends(get_repository(ProductsRepository)),
) -> ProductPublic:
    product = await product_repo.get_product_by_id(id=id)

    if not product:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="no product found with that id.")

    return product

@router.post("/", response_model=ProductPublic, name="products:create-product", status_code=HTTP_201_CREATED)
async def create_new_product(
    new_product: ProductCreate = Body(..., embed=True),
    products_repo: ProductsRepository = Depends(get_repository(ProductsRepository)),
) -> ProductPublic:
    created_product = await products_repo.create_product(new_product=new_product)
    return created_product