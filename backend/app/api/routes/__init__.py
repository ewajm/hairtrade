from fastapi.routing import APIRouter


from app.api.routes.products import router as products_router

router = APIRouter()

router.include_router(products_router, prefix="/products", tags="products")