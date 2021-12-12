from fastapi.routing import APIRouter


from app.api.routes.products import router as products_router
from app.api.routes.users import router as users_router
from app.api.routes.profiles import router as profiles_router
from app.api.routes.items import router as user_product_router

router = APIRouter()

router.include_router(products_router, prefix="/products", tags=["products"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
router.include_router(user_product_router, prefix="/user_products", tags=["user_products"])