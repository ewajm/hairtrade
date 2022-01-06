from typing import List, Callable

import pytest

from httpx import AsyncClient
from fastapi import FastAPI, status
from databases import Database

from app.models.item import ItemCreate, ItemInDB
from app.models.user import UserInDB
from app.models.offer import OfferCreate, OfferUpdate, OfferInDB, OfferPublic


pytestmark = pytest.mark.asyncio


class TestOffersRoutes:
    """
    Make sure all offers routes don't return 404s
    """

    async def test_routes_exist(self, app: FastAPI, client: AsyncClient, test_item:ItemInDB) -> None:
        res = await client.post(app.url_path_for("offers:create-offer", item_id=1))
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.get(app.url_path_for("offers:list-offers-for-item", item_id=1))
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.get(app.url_path_for("offers:get-offer-from-user", item_id=1, username="bradpitt"))
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.put(app.url_path_for("offers:accept-offer-from-user", item_id=1, username="bradpitt"))
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.put(app.url_path_for("offers:cancel-offer-from-user", item_id=1))
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.delete(app.url_path_for("offers:rescind-offer-from-user", item_id=1))
        assert res.status_code != status.HTTP_404_NOT_FOUND

class TestCreateOffers:
    async def test_user_can_successfully_create_offer_for_other_users_cleaning_job(
        self, app: FastAPI, create_authorized_client: Callable, test_item: ItemInDB, test_user3: UserInDB,
    ) -> None:
        authorized_client = create_authorized_client(user=test_user3)
        res = await authorized_client.post(app.url_path_for("offers:create-offer", item_id=test_item.id))
        assert res.status_code == status.HTTP_201_CREATED
        offer = OfferPublic(**res.json())
        assert offer.user_id == test_user3.id
        assert offer.item_id == test_item.id
        assert offer.status == "pending"

    async def test_user_cant_create_duplicate_offers(
        self, app: FastAPI, create_authorized_client: Callable, test_item: ItemInDB, test_user4: UserInDB,
    ) -> None:
        authorized_client = create_authorized_client(user=test_user4)
        res = await authorized_client.post(app.url_path_for("offers:create-offer", item_id=test_item.id))
        assert res.status_code == status.HTTP_201_CREATED
        res = await authorized_client.post(app.url_path_for("offers:create-offer", item_id=test_item.id))
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    async def test_user_unable_to_create_offer_for_their_own_cleaning_job(
        self, app: FastAPI, authorized_client: AsyncClient, test_user: UserInDB, test_item: ItemInDB,
    ) -> None:
        res = await authorized_client.post(app.url_path_for("offers:create-offer", item_id=test_item.id))
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        
    async def test_unauthenticated_users_cant_create_offers(
        self, app: FastAPI, client: AsyncClient, test_item: ItemInDB,
    ) -> None:
        res = await client.post(app.url_path_for("offers:create-offer", item_id=test_item.id))
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
    @pytest.mark.parametrize(
        "id, status_code", ((5000000, 404), (-1, 422), (None, 422)),
    )
    async def test_wrong_id_gives_proper_error_status(
        self, app: FastAPI, create_authorized_client: Callable, test_user5: UserInDB, id: int, status_code: int,
    ) -> None:
        authorized_client = create_authorized_client(user=test_user5)
        res = await authorized_client.post(app.url_path_for("offers:create-offer", item_id=id))
        assert res.status_code == status_code