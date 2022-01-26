from typing import List
from venv import create

from databases import Database
from app.db.metadata import TradeEval

from app.db.repositories.base import BaseRepository
from app.db.repositories.offers import OffersRepository

from app.models.trade import TradeInDB
from app.models.user import UserInDB
from app.models.evaluation import EvaluationCreate, EvaluationUpdate, EvaluationInDB, EvaluationAggregate

from sqlalchemy.sql import func

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

    def get_trader_evaluation_for_trade(self, *, trade: TradeInDB, trader: UserInDB) -> TradeEval:
        evaluation = self.db.query(TradeEval).filter(TradeEval.trade_id == trade.id, TradeEval.trader_id == trader.id).first()
        if not evaluation:
            return None
        return evaluation


    def list_evaluations_for_trader(self, *, trader: UserInDB) -> List[EvaluationInDB]:
        evaluations = self.db.query(TradeEval).filter(TradeEval.trader_id == trader.id).all()
        return evaluations

    def get_trader_aggregates(self, *, trader: UserInDB):
        return self.db.query(func.avg(TradeEval.responsiveness).label("avg_responsiveness"),
                             func.avg(TradeEval.demeanor).label("avg_demeanor"),
                             func.avg(TradeEval.overall_rating).label("avg_overall_rating"),
                             func.min(TradeEval.overall_rating).label("min_overall_rating"),
                             func.max(TradeEval.overall_rating).label("max_overall_rating"),
                             func.count(TradeEval.trade_id).label("total_evaluations"),
                             func.count(TradeEval.no_show).filter(TradeEval.no_show).label("total_no_show"),
                             func.count(TradeEval.overall_rating).filter(TradeEval.overall_rating == 1).label("one_stars"),
                             func.count(TradeEval.overall_rating).filter(TradeEval.overall_rating == 2).label("two_stars"),
                             func.count(TradeEval.overall_rating).filter(TradeEval.overall_rating == 3).label("three_stars"),
                             func.count(TradeEval.overall_rating).filter(TradeEval.overall_rating == 4).label("four_stars"),
                             func.count(TradeEval.overall_rating).filter(TradeEval.overall_rating == 5).label("five_stars"),
                              ).filter(TradeEval.trader_id == trader.id).one_or_none()
