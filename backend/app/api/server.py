import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import settings
from app.core.config import DATABASE_URL
from app.core.config import DATABASE_URL
# try:
#     settings.db_url
# except AttributeError:
#     settings.init()
#     settings.db_url = DATABASE_URL


from app.core import config  
from app.api.routes import router as api_router

def get_application():
    app = FastAPI(title=config.PROJECT_NAME, version=config.VERSION)  

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")
    return app

app = get_application()

@app.get("/")
async def root():
    return {"message":"Hello World"}