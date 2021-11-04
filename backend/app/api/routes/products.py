from typing import List
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_all_products() -> List[dict]:
    products = [
        {"id":1, "name": "Carol's Daughter Curl Refresher Spray", "product_type": "Spray", "what_do":"trade"},
        {"id":1, "name": "Ouidad Smoothing Creme", "product_type": "creme", "what_do":"giveaway"}
    ]

    return products
