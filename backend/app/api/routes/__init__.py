from fastapi.routing import APIRouter


from app.api.routes.products import router as products_router
from app.api.routes.users import router as users_router
from app.api.routes.profiles import router as profiles_router
from app.api.routes.trades import router as trade_router
from app.api.routes.offers import router as offers_router
from app.api.routes.evaluations import router as evaluations_router    

router = APIRouter()

router.include_router(products_router, prefix="/products", tags=["products"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
router.include_router(trade_router, prefix="/trade", tags=["trades"])
router.include_router(offers_router, prefix="/trade/{trade_id}/offers", tags=["offers"])  
router.include_router(evaluations_router, prefix="/users/{username}/evaluations", tags=["evaluations"])  
