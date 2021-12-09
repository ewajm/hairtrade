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

from app.core.config import DATABASE_URL, SECRET_KEY, JWT_TOKEN_PREFIX
from app import settings
settings.init()
settings.db_url = f"{DATABASE_URL}_test"

from app.services import auth_service

from app.db.repositories.products import ProductsRepository
from app.db.repositories.users import UsersRepository
from app.models.product import ProductCreate, ProductInDB, ProductType, WhatDo
from app.models.user import UserCreate, UserInDB
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
    return ProductInDB.from_orm(product_repo.create_product(new_product=new_product))

@pytest.fixture
async def test_user(db: session.Session) -> UserInDB:
    new_user = UserCreate(
        email="lebron@james.io",
        username="lebronjames",
        password="heatcavslakers",
    )
    user_repo = UsersRepository(db)
    existing_user = user_repo.get_user_by_email(email=new_user.email)
    if existing_user:
        return existing_user
    return UserInDB.from_orm(user_repo.register_new_user(new_user=new_user))

@pytest.fixture
def authorized_client(client: AsyncClient, test_user: UserInDB) -> AsyncClient:
    access_token = auth_service.create_access_token_for_user(user=test_user, secret_key=str(SECRET_KEY))
    client.headers = {
        **client.headers,
        "Authorization": f"{JWT_TOKEN_PREFIX} {access_token}",
    }
    return client

@pytest.fixture
async def test_user2(db: session.Session) -> UserInDB:
    new_user = UserCreate(
        email="serena@williams.io",
        username="serenawilliams",
        password="tennistwins",
    )
    user_repo = UsersRepository(db)
    existing_user = user_repo.get_user_by_email(email=new_user.email)
    if existing_user:
        return existing_user
    return UserInDB.from_orm(user_repo.register_new_user(new_user=new_user))