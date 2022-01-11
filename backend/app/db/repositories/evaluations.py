from typing import List

from databases import Database

from app.db.repositories.base import BaseRepository
from app.db.repositories.offers import OffersRepository

from app.models.trade import TradeInDB
from app.models.user import UserInDB
from app.models.evaluation import EvaluationCreate, EvaluationUpdate, EvaluationInDB, EvaluationAggregate


class EvaluationsRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.offers_repo = OffersRepository(db)

