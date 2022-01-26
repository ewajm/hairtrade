from itertools import product
import random
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

from app.db.repositories.offers import OffersRepository
from app.models.offer import OfferCreate, OfferUpdate
from app.services import auth_service
from app.models.trade import TradeCreate, TradeInDB, Size, WhatDo
from app.db.repositories.products import ProductsRepository
from app.db.repositories.users import UsersRepository
from app.models.product import ProductCreate, ProductInDB, ProductType
from app.models.user import UserCreate, UserInDB
from app.db.database import SessionLocal
from app.db.database import engine
from app.db.metadata import Trade
from app.db.repositories.trades import TradeRepository
from app.db.repositories.evaluations import EvaluationsRepository
from app.models.evaluation import EvaluationCreate


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
async def test_trade(test_user:UserInDB, test_product:ProductInDB, db:session.Session):
    new_trade = TradeCreate(
        product_id = test_product.id,
        what_do = WhatDo.trade,
        comment = "didn't like smell",
        size = Size.travel
    )
    existing_trade = db.query(Trade).filter(
        Trade.user_id == test_user.id, 
        Trade.product_id == test_product.id,
        Trade.what_do == "trade",
        Trade.comment == "didn't like smell",
        Trade.size == "travel",
    ).first()
    if existing_trade:
        return existing_trade
    trade_repo = TradeRepository(db)
    return trade_repo.create_trade(trade_create= new_trade, user_id=test_user.id)

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

@pytest.fixture
def test_trade_with_offers(db: session.Session, test_product: ProductInDB, test_user2: UserInDB, test_user_list: List[UserInDB]) -> TradeInDB:
    trade_repo = TradeRepository(db)
    offers_repo = OffersRepository(db)
    new_trade = TradeCreate(product_id = test_product.id)
    created_trade = trade_repo.create_trade(trade_create=new_trade, user_id=test_user2.id) 
    for user in test_user_list:
        offers_repo.create_offer_for_trade(
            new_offer=OfferCreate(trade_id=created_trade.id, user_id=user.id)
        )
    return TradeInDB.from_orm(created_trade)

@pytest.fixture
def test_trade_with_accepted_offer(
    db: session.Session, test_product: ProductInDB, test_user2: UserInDB, test_user3: UserInDB, test_user_list: List[UserInDB]
) -> TradeInDB:
    trade_repo = TradeRepository(db)
    offers_repo = OffersRepository(db)
    new_trade = TradeCreate(product_id = test_product.id)
    created_trade = trade_repo.create_trade(trade_create=new_trade, user_id=test_user2.id) 
    offers = []
    for user in test_user_list:
        offers.append(
            offers_repo.create_offer_for_trade(
                new_offer=OfferCreate(trade_id=created_trade.id, user_id=user.id)
            )
        )
    offers_repo.accept_offer(
        offer=[o for o in offers if o.user_id == test_user3.id][0], offer_update=OfferUpdate(status="accepted")
    )
    return TradeInDB.from_orm(created_trade)

def create_trade_with_evaluated_offer_helper(
    db: session.Session,
    owner: UserInDB,
    receiver: UserInDB,
    product_create: ProductCreate,
    evaluation_create: EvaluationCreate,
) -> TradeInDB:
    product_repo = ProductsRepository(db)
    trade_repo = TradeRepository(db)
    offers_repo = OffersRepository(db)
    evals_repo = EvaluationsRepository(db)
    existing_product = product_repo.get_product_by_name(name = product_create.product_name)
    if existing_product:
        return trade_repo.get_trades_by_product_id_and_user_id(product_id=existing_product.id, user_id=owner.id)[0]
    created_product = product_repo.create_product(new_product=product_create)
    trade_create = TradeCreate(size="regular", comment="didn't like", product_id = created_product.id)
    created_trade = trade_repo.create_trade(trade_create=trade_create, user_id=owner.id)
    offer = offers_repo.create_offer_for_trade(
        new_offer=OfferCreate(trade_id=created_trade.id, user_id=receiver.id)
    )
    offers_repo.accept_offer(offer=offer, offer_update=OfferUpdate(status="accepted"))
    evals_repo.create_evaluation_for_trade(
        evaluation_create=evaluation_create, trade=created_trade, trader=owner, reviewer=receiver,
    )
    return created_trade

@pytest.fixture
def test_list_of_trades_with_evaluated_offer(
    db: session.Session, test_user2: UserInDB, test_user3: UserInDB
) -> List[TradeInDB]:
    return [
        create_trade_with_evaluated_offer_helper(
            db=db,
            owner=test_user2,
            receiver=test_user3,
            product_create=ProductCreate(
                product_name=f"test product - {i}",
                brand=f"test brand - {i}",
                description=f"test description - {i}",
                type=ProductType.dunno,
            ),
            evaluation_create=EvaluationCreate(
                responsiveness=random.randint(0, 5),
                demeanor=random.randint(0, 5),
                overall_rating=random.randint(0, 5),
            ),
        )
        for i in range(5)
    ]