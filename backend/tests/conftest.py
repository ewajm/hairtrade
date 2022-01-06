from typing import Callable, List
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
from app.models.item import ItemCreate, Size, WhatDo
from app.db.repositories.products import ProductsRepository
from app.db.repositories.users import UsersRepository
from app.models.product import ProductCreate, ProductInDB, ProductType
from app.models.user import UserCreate, UserInDB
from app.db.database import SessionLocal
from app.db.database import engine
from app.db.metadata import Item
from app.db.repositories.items import ItemRepository


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
    )
    existing_product = product_repo.get_product_by_name(name = new_product.product_name)
    if existing_product:
        return existing_product
    return product_repo.create_product(new_product=new_product)

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
    return user_repo.register_new_user(new_user=new_user)

@pytest.fixture
def authorized_client(client: AsyncClient, test_user: UserInDB) -> AsyncClient:
    access_token = auth_service.create_access_token_for_user(user=test_user, secret_key=str(SECRET_KEY))
    client.headers = {
        **client.headers,
        "Authorization": f"{JWT_TOKEN_PREFIX} {access_token}",
    }
    return client

@pytest.fixture
def test_user2(db: session.Session):
    new_user = UserCreate(
        email="serena@williams.io",
        username="serenawilliams",
        password="tennistwins",
    )
    user_repo = UsersRepository(db)
    existing_user = user_repo.get_user_by_email(email=new_user.email)
    if existing_user:
        return existing_user
    return user_repo.register_new_user(new_user=new_user)

def user_fixture_helper(*, db: session.Session, new_user: UserCreate) -> UserInDB:
    user_repo = UsersRepository(db)
    existing_user = user_repo.get_user_by_email(email=new_user.email)
    if existing_user:
        return existing_user
    return user_repo.register_new_user(new_user=new_user)

@pytest.fixture
async def test_item(test_user:UserInDB, test_product:ProductInDB, db:session.Session):
    new_item = ItemCreate(
        product_id = test_product.id,
        what_do = WhatDo.trade,
        comment = "didn't like smell",
        size = Size.travel
    )
    existing_item = db.query(Item).filter(
        Item.user_id == test_user.id, 
        Item.product_id == test_product.id,
        Item.what_do == "trade",
        Item.comment == "didn't like smell",
        Item.size == "travel",
    ).first()
    if existing_item:
        return existing_item
    item_repo = ItemRepository(db)
    return item_repo.create_item(item_create= new_item, user_id=test_user.id)

@pytest.fixture
def test_user3(db: session.Session) -> UserInDB:
    new_user = UserCreate(email="brad@pitt.io", username="bradpitt", password="adastra")
    return user_fixture_helper(db=db, new_user=new_user)
@pytest.fixture
def test_user4(db: session.Session) -> UserInDB:
    new_user = UserCreate(email="jennifer@lopez.io", username="jlo", password="jennyfromtheblock")
    return user_fixture_helper(db=db, new_user=new_user)
@pytest.fixture
def test_user5(db: session.Session) -> UserInDB:
    new_user = UserCreate(email="bruce@lee.io", username="brucelee", password="martialarts")
    return user_fixture_helper(db=db, new_user=new_user)
@pytest.fixture
def test_user6(db: session.Session) -> UserInDB:
    new_user = UserCreate(email="kal@penn.io", username="kalpenn", password="haroldandkumar")
    return user_fixture_helper(db=db, new_user=new_user)
@pytest.fixture
async def test_user_list(
    test_user3: UserInDB, test_user4: UserInDB, test_user5: UserInDB, test_user6: UserInDB,
) -> List[UserInDB]:
    return [test_user3, test_user4, test_user5, test_user6]

@pytest.fixture
def create_authorized_client(client: AsyncClient) -> Callable:
    def _create_authorized_client(*, user: UserInDB) -> AsyncClient:
        access_token = auth_service.create_access_token_for_user(user=user, secret_key=str(SECRET_KEY))
        client.headers = {
            **client.headers,
            "Authorization": f"{JWT_TOKEN_PREFIX} {access_token}",
        }
        return client
    return _create_authorized_client

