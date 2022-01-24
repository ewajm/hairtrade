from typing import List
from venv import create

from databases import Database
from app.db.metadata import TradeEval

from app.db.repositories.base import BaseRepository
from app.db.repositories.offers import OffersRepository

from app.models.trade import TradeInDB
from app.models.user import UserInDB
from app.models.evaluation import EvaluationCreate, EvaluationUpdate, EvaluationInDB, EvaluationAggregate


class EvaluationsRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.offers_repo = OffersRepository(db)

    def create_evaluation_for_trade(
        self, *, evaluation_create: EvaluationCreate, trade: TradeInDB, trader: UserInDB, reviewer: UserInDB
    ) -> EvaluationInDB:
        created_evaluation = TradeEval(**evaluation_create.dict(), trade_id = trade.id, reviewer_id = reviewer.id, trader_id = trader.id)
        print(created_evaluation.as_dict())
        self.db.add(created_evaluation)
        # also mark offer as completed
        self.offers_repo.mark_offer_completed(trade=trade, recipient=reviewer)
        self.db.commit()
        self.db.refresh(created_evaluation)
        return created_evaluation