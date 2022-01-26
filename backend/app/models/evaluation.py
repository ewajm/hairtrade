from enum import Enum
from typing import Optional, Union

from pydantic import conint, confloat

from app.models.core import DateTimeModelMixin, CoreModel
from app.models.user import UserPublic
from app.models.trade import TradePublic


class EvaluationBase(CoreModel):
    no_show: bool = False
    responsiveness: Optional[conint(ge=0, le=5)]
    demeanor: Optional[conint(ge=0, le=5)]
    overall_rating: Optional[conint(ge=0, le=5)]


class EvaluationCreate(EvaluationBase):
    overall_rating: conint(ge=0, le=5)


class EvaluationUpdate(EvaluationBase):
    pass


class EvaluationInDB(DateTimeModelMixin, EvaluationBase):
    trader_id: int
    trade_id: int
    reviewer_id: int

    class Config:
        orm_mode = True


class EvaluationPublic(EvaluationInDB):
    trade: Optional[TradePublic]
    reviewer: Optional[UserPublic]
    trader: Optional[UserPublic]

    class Config:
        orm_mode = True

class EvaluationAggregate(CoreModel):
    avg_responsiveness: confloat(ge=0, le=5)
    avg_demeanor: confloat(ge=0, le=5)
    avg_overall_rating: confloat(ge=0, le=5)
    max_overall_rating: conint(ge=0, le=5)
    min_overall_rating: conint(ge=0, le=5)
    one_stars: conint(ge=0)
    two_stars: conint(ge=0)
    three_stars: conint(ge=0)
    four_stars: conint(ge=0)
    five_stars: conint(ge=0)
    total_evaluations: conint(ge=0)
    total_no_show: conint(ge=0)

    class Config:
        orm_mode = True
