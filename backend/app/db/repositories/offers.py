from typing import List

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.db.metadata import Offer

from app.db.repositories.base import BaseRepository
from app.models.offer import OfferCreate, OfferUpdate, OfferInDB


class OffersRepository(BaseRepository):
    def create_offer_for_item(self, *, new_offer: OfferCreate) -> OfferInDB:
        try:
            print(new_offer.dict())
            created_offer = Offer(**new_offer.dict())
            self.db.add(created_offer)
            self.db.commit()
            self.db.refresh(created_offer)
            return created_offer
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Users aren't allowed create more than one offer for a item job.",
            )

