from typing import List, Callable

import pytest
import random

from httpx import AsyncClient
from fastapi import FastAPI, status
from databases import Database
from sqlalchemy.orm import session
from app.db.metadata import Trade
from app.db.repositories.offers import OffersRepository

from app.models.trade import TradeCreate, TradeInDB
from app.models.user import UserInDB
from app.models.offer import OfferCreate, OfferUpdate, OfferInDB, OfferPublic


pytestmark = pytest.mark.asyncio


class TestOffersRoutes:
    """
    Make sure all offers routes don't return 404s
    """

    async def test_routes_exist(self, app: FastAPI, client: AsyncClient, test_trade:TradeInDB) -> None:
        res = await client.post(app.url_path_for("offers:create-offer", trade_id=1))
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.get(app.url_path_for("offers:list-offers-for-trade", trade_id=1))
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.get(app.url_path_for("offers:get-offer-from-user", trade_id=1, username="bradpitt"))
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.put(app.url_path_for("offers:accept-offer-from-user", trade_id=1, username="bradpitt"))
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.put(app.url_path_for("offers:cancel-offer-from-user", trade_id=1))
        assert res.status_code != status.HTTP_404_NOT_FOUND

        res = await client.delete(app.url_path_for("offers:rescind-offer-from-user", trade_id=1))
        assert res.status_code != status.HTTP_404_NOT_FOUND

class TestCreateOffers:
    async def test_user_can_successfully_create_offer_for_other_users_cleaning_job(
        self, app: FastAPI, create_authorized_client: Callable, test_trade: Trade, test_user3: UserInDB,
    ) -> None:
        print(test_trade.as_dict())
        authorized_client = create_authorized_client(user=test_user3)
        res = await authorized_client.post(app.url_path_for("offers:create-offer", trade_id=test_trade.id))
        assert res.status_code == status.HTTP_201_CREATED
        offer = OfferPublic(**res.json())
        assert offer.user_id == test_user3.id
        assert offer.trade_id == test_trade.id
        assert offer.status == "pending"

    async def test_user_cant_create_duplicate_offers(
        self, app: FastAPI, create_authorized_client: Callable, test_trade: TradeInDB, test_user4: UserInDB,
    ) -> None:
        authorized_client = create_authorized_client(user=test_user4)
        res = await authorized_client.post(app.url_path_for("offers:create-offer", trade_id=test_trade.id))
        assert res.status_code == status.HTTP_201_CREATED
        res = await authorized_client.post(app.url_path_for("offers:create-offer", trade_id=test_trade.id))
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    async def test_user_unable_to_create_offer_for_their_own_cleaning_job(
        self, app: FastAPI, authorized_client: AsyncClient, test_user: UserInDB, test_trade: TradeInDB,
    ) -> None:
        res = await authorized_client.post(app.url_path_for("offers:create-offer", trade_id=test_trade.id))
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        
    async def test_unauthenticated_users_cant_create_offers(
        self, app: FastAPI, client: AsyncClient, test_trade: TradeInDB,
    ) -> None:
        res = await client.post(app.url_path_for("offers:create-offer", trade_id=test_trade.id))
        assert res.status_code == status.HTTP_401_UNAUTHORIZED
    @pytest.mark.parametrize(
        "id, status_code", ((5000000, 404), (-1, 422), (None, 422)),
    )
    async def test_wrong_id_gives_proper_error_status(
        self, app: FastAPI, create_authorized_client: Callable, test_user5: UserInDB, id: int, status_code: int,
    ) -> None:
        authorized_client = create_authorized_client(user=test_user5)
        res = await authorized_client.post(app.url_path_for("offers:create-offer", trade_id=id))
        assert res.status_code == status_code

class TestGetOffers:
    async def test_trade_owner_can_get_offer_from_user(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user2: UserInDB,
        test_user_list: List[UserInDB],
        test_trade_with_offers: TradeInDB,
    ) -> None:
        authorized_client = create_authorized_client(user=test_user2)
        selected_user = random.choice(test_user_list)
        res = await authorized_client.get(
            app.url_path_for(
                "offers:get-offer-from-user", 
                trade_id=test_trade_with_offers.id, 
                username=selected_user.username,
            )
        )
        assert res.status_code == status.HTTP_200_OK
        offer = OfferPublic(**res.json())
        assert offer.user_id == selected_user.id

    async def test_offer_owner_can_get_own_offer(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user_list: List[UserInDB],
        test_trade_with_offers: TradeInDB,
    ) -> None:
        first_test_user = test_user_list[0]
        authorized_client = create_authorized_client(user=first_test_user)        
        res = await authorized_client.get(
            app.url_path_for(
                "offers:get-offer-from-user",
                trade_id=test_trade_with_offers.id,
                username=first_test_user.username,
            )
        )
        assert res.status_code == status.HTTP_200_OK
        offer = OfferPublic(**res.json())
        assert offer.user_id == first_test_user.id    

    async def test_other_authenticated_users_cant_view_offer_from_user(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user_list: List[UserInDB],
        test_trade_with_offers: TradeInDB,
    ) -> None:
        first_test_user = test_user_list[0]
        second_test_user = test_user_list[1]
        authorized_client = create_authorized_client(user=first_test_user)
        res = await authorized_client.get(
            app.url_path_for(
                "offers:get-offer-from-user",
                trade_id=test_trade_with_offers.id,
                username=second_test_user.username,
            )
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN

    async def test_trade_owner_can_get_all_offers_for_trades(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user2: UserInDB,
        test_user_list: List[UserInDB],
        test_trade_with_offers: TradeInDB,
    ) -> None:
        authorized_client = create_authorized_client(user=test_user2)
        res = await authorized_client.get(
            app.url_path_for("offers:list-offers-for-trade", trade_id=test_trade_with_offers.id)
        )
        assert res.status_code == status.HTTP_200_OK
        for offer in res.json():
            assert offer["user_id"] in [user.id for user in test_user_list]

    async def test_non_owners_forbidden_from_fetching_all_offers_for_trade(
        self, app: FastAPI, authorized_client: AsyncClient, test_trade_with_offers: TradeInDB,
    ) -> None:
        res = await authorized_client.get(
            app.url_path_for("offers:list-offers-for-trade", trade_id=test_trade_with_offers.id)
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN

class TestAcceptOffers:

    async def test_trade_owner_can_accept_offer_successfully(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user2: UserInDB,
        test_user_list: List[UserInDB],
        test_trade_with_offers: TradeInDB,
    ) -> None:
        selected_user = random.choice(test_user_list)
        authorized_client = create_authorized_client(user=test_user2)
        res = await authorized_client.put(
            app.url_path_for(
                "offers:accept-offer-from-user",
                trade_id=test_trade_with_offers.id,
                username=selected_user.username,
            )
        )
        assert res.status_code == status.HTTP_200_OK
        accepted_offer = OfferPublic(**res.json())
        assert accepted_offer.status == "accepted"
        assert accepted_offer.user_id == selected_user.id
        assert accepted_offer.trade_id == test_trade_with_offers.id

    async def test_non_owner_forbidden_from_accepting_offer_for_trade(
        self,
        app: FastAPI,
        authorized_client: AsyncClient,
        test_user_list: List[UserInDB],
        test_trade_with_offers: TradeInDB,
    ) -> None:
        selected_user = random.choice(test_user_list)
        res = await authorized_client.put(
            app.url_path_for(
                "offers:accept-offer-from-user",
                trade_id=test_trade_with_offers.id,
                username=selected_user.username,
            )
        )
        assert res.status_code == status.HTTP_403_FORBIDDEN

    async def test_trade_owner_cant_accept_multiple_offers(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user2: UserInDB,
        test_user_list: List[UserInDB],
        test_trade_with_offers: TradeInDB,
    ) -> None:
        authorized_client = create_authorized_client(user=test_user2)
        res = await authorized_client.put(
            app.url_path_for(
                "offers:accept-offer-from-user",
                trade_id=test_trade_with_offers.id,
                username=test_user_list[0].username,
            )
        )
        assert res.status_code == status.HTTP_200_OK
        res = await authorized_client.put(
            app.url_path_for(
                "offers:accept-offer-from-user",
                trade_id=test_trade_with_offers.id,
                username=test_user_list[1].username,
            )
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    async def test_accepting_one_offer_rejects_all_other_offers(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user2: UserInDB,
        test_user_list: List[UserInDB],
        test_trade_with_offers: TradeInDB,
    ) -> None:
        selected_user = random.choice(test_user_list)
        authorized_client = create_authorized_client(user=test_user2)
        res = await authorized_client.put(
            app.url_path_for(
                "offers:accept-offer-from-user",
                trade_id=test_trade_with_offers.id,
                username=selected_user.username,
            )
        )
        assert res.status_code == status.HTTP_200_OK
        res = await authorized_client.get(
            app.url_path_for("offers:list-offers-for-trade", trade_id=test_trade_with_offers.id)
        )
        assert res.status_code == status.HTTP_200_OK
        offers = [OfferPublic(**o) for o in res.json()]
        for offer in offers:
            if offer.user_id == selected_user.id:
                assert offer.status == "accepted"
            else:
                assert offer.status == "rejected"

class TestCancelOffers:
    async def test_user_can_cancel_offer_after_it_has_been_accepted(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user3: UserInDB,
        test_trade_with_accepted_offer: TradeInDB,
    ) -> None:
        accepted_user_client = create_authorized_client(user=test_user3)
        res = await accepted_user_client.put(
            app.url_path_for("offers:cancel-offer-from-user", trade_id=test_trade_with_accepted_offer.id)
        )
        assert res.status_code == status.HTTP_200_OK
        cancelled_offer = OfferPublic(**res.json())
        assert cancelled_offer.status == "cancelled"
        assert cancelled_offer.user_id == test_user3.id
        assert cancelled_offer.trade_id == test_trade_with_accepted_offer.id

    async def test_only_accepted_offers_can_be_cancelled(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user4: UserInDB,
        test_trade_with_accepted_offer: TradeInDB,
    ) -> None:
        selected_user_client = create_authorized_client(user=test_user4)
        res = await selected_user_client.put(
            app.url_path_for("offers:cancel-offer-from-user", trade_id=test_trade_with_accepted_offer.id)
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    async def test_cancelling_offer_sets_all_others_to_pending(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user3: UserInDB,
        test_trade_with_accepted_offer: TradeInDB,
        db:session.Session
    ) -> None:
        accepted_user_client = create_authorized_client(user=test_user3)
        res = await accepted_user_client.put(
            app.url_path_for("offers:cancel-offer-from-user", trade_id=test_trade_with_accepted_offer.id)
        )
        assert res.status_code == status.HTTP_200_OK
        offers_repo = OffersRepository(db)
        offers = offers_repo.list_offers_for_trade(trade=test_trade_with_accepted_offer)
        for offer in offers:
            if offer.user_id == test_user3.id:
                assert offer.status == "cancelled"
            else:
                assert offer.status == "pending"

class TestRescindOffers:

    async def test_user_can_successfully_rescind_pending_offer(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user4: UserInDB,
        test_user_list: List[UserInDB],
        test_trade_with_offers: TradeInDB,
        db: session.Session
    ) -> None:
        authorized_client = create_authorized_client(user=test_user4)
        res = await authorized_client.delete(
            app.url_path_for("offers:rescind-offer-from-user", trade_id=test_trade_with_offers.id)
        )
        assert res.status_code == status.HTTP_200_OK
        offers_repo = OffersRepository(db)
        offers = offers_repo.list_offers_for_trade(trade=test_trade_with_offers)
        user_ids = [user.id for user in test_user_list]
        for offer in offers:
            assert offer.user_id in user_ids
            assert offer.user_id != test_user4.id

    async def test_users_cannot_rescind_accepted_offers(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user3: UserInDB,
        test_trade_with_accepted_offer: TradeInDB,
    ) -> None:
        authorized_client = create_authorized_client(user=test_user3)
        res = await authorized_client.delete(
            app.url_path_for("offers:rescind-offer-from-user", trade_id=test_trade_with_accepted_offer.id)
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    async def test_users_cannot_rescind_cancelled_offers(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user3: UserInDB,
        test_trade_with_accepted_offer: TradeInDB,
    ) -> None:
        authorized_client = create_authorized_client(user=test_user3)
        res = await authorized_client.put(
            app.url_path_for("offers:cancel-offer-from-user", trade_id=test_trade_with_accepted_offer.id)
        )
        assert res.status_code == status.HTTP_200_OK
        res = await authorized_client.delete(
            app.url_path_for("offers:rescind-offer-from-user", trade_id=test_trade_with_accepted_offer.id)
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST

    async def test_users_cannot_rescind_rejected_offers(
        self,
        app: FastAPI,
        create_authorized_client: Callable,
        test_user4: UserInDB,
        test_trade_with_accepted_offer: TradeInDB,
    ) -> None:
        authorized_client = create_authorized_client(user=test_user4)
        res = await authorized_client.delete(
            app.url_path_for("offers:rescind-offer-from-user", trade_id=test_trade_with_accepted_offer.id)
        )
        assert res.status_code == status.HTTP_400_BAD_REQUEST