from typing import List

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.db.metadata import Offer

from app.db.repositories.base import BaseRepository
from app.models.item import ItemInDB
from app.models.offer import OfferCreate, OfferUpdate, OfferInDB
from app.models.user import UserInDB


class OffersRepository(BaseRepository):
    def create_offer_for_item(self, *, new_offer: OfferCreate) -> OfferInDB:

        print(new_offer.dict())
        created_offer = Offer(**new_offer.dict())
        self.db.add(created_offer)
        self.db.commit()
        self.db.refresh(created_offer)
        return created_offer


    def list_offers_for_item(self, *, item: ItemInDB) -> List[OfferInDB]:
        offers = self.db.query(Offer).filter(Offer.item_id == item.id).all()
        return offers

    def get_offer_for_item_from_user(self, *, item: ItemInDB, user: UserInDB) -> OfferInDB:
        offer_record = self.db.query(Offer).filter(Offer.item_id == item.id, Offer.user_id == user.id).first()
        if not offer_record:
            return None
        return offer_record