import warnings
import os
import time

import pytest
from asgi_lifespan import LifespanManager

from fastapi import FastAPI
from httpx import AsyncClient

import alembic
from alembic.config import Config
from sqlalchemy.orm import session
from sqlalchemy.orm import close_all_sessions

from app.core.config import DATABASE_URL
from app import settings

settings.init()
settings.db_url = f"{DATABASE_URL}_test"

from app.db.repositories.products import ProductsRepository
from app.models.product import ProductCreate, ProductType, WhatDo
from app.db.database import SessionLocal
from app.db.database import engine


# Apply migrations at beginning and end of testing session
@pytest.fixture(scope="session")
def apply_migrations():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    os.environ["TESTING"] = "1"
    config = Config("alembic.ini")
    alembic.command.upgrade(config, "head")
    yield
    close_all_sessions()
    engine.dispose()
    alembic.command.downgrade(config, "base")


# Create a new application for testing
@pytest.fixture
def app(apply_migrations: None) -> FastAPI:
    from app.api.server import get_application

    return  get_application()


# Grab a reference to our database when needed
@pytest.fixture
def db() -> session.Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Make requests in our tests
@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    async with LifespanManager(app):
        async with AsyncClient(
            app=app,
            base_url="http://testserver",
            headers={"Content-Type": "application/json"}
        ) as client:
            yield client

@pytest.fixture
async def test_product(db:session.Session):
    product_repo = ProductsRepository(db)
    new_product = ProductCreate(
        product_name="fake_product",
        description="fake description",
        type=ProductType.cream,
        brand="fake brand",
        what_do=WhatDo.sell,
        price=9.99
    )
    return product_repo.create_product(new_product=new_product)