from typing import List

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from sqlalchemy.sql.expression import false
from app.db.metadata import Offer

from app.db.repositories.base import BaseRepository
from app.models.trade import TradeInDB
from app.models.offer import OfferCreate, OfferUpdate, OfferInDB
from app.models.user import UserInDB


class OffersRepository(BaseRepository):
    def create_offer_for_trade(self, *, new_offer: OfferCreate) -> Offer:
        created_offer = Offer(**new_offer.dict())
        self.db.add(created_offer)
        self.db.commit()
        self.db.refresh(created_offer)
        return created_offer


    def list_offers_for_trade(self, *, trade: TradeInDB) -> List[Offer]:
        offers = self.db.query(Offer).filter(Offer.trade_id == trade.id).all()
        return offers

    def get_offer_for_trade_from_user(self, *, trade: TradeInDB, user: UserInDB) -> Offer:
        offer_record = self.db.query(Offer).filter(Offer.trade_id == trade.id, Offer.user_id == user.id).first()
        if not offer_record:
            return None
        return offer_record

    def accept_offer(self, *, offer: Offer, offer_update: OfferUpdate) -> Offer:
        offer.status = offer_update.status   

        self.db.add(offer)
        self.db.query(Offer).filter(Offer.trade_id == offer.trade_id, Offer.user_id != offer.user_id).\
            update({Offer.status: "rejected"}, synchronize_session=False)
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def cancel_offer(self, *, offer: Offer, offer_update: OfferUpdate) -> Offer:
        offer.status = offer_update.status   

        self.db.add(offer)
        self.db.query(Offer).filter(Offer.trade_id == offer.trade_id, Offer.user_id != offer.user_id, Offer.status == "rejected").\
            update({Offer.status: "pending"}, synchronize_session=False)
        self.db.commit()
        self.db.refresh(offer)
        return offer

    def rescind_offer(self, *, offer:Offer):
        self.db.delete(offer)
        self.db.commit()
        return offer