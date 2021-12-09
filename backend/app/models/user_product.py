from enum import Enum
from typing import Optional
from app.models.core import CoreModel, DateTimeModelMixin

from app.models.product import ProductPublic, ProductType
from app.models.user import UserPublic

class WhatDo(str, Enum):
    trade = "trade"
    sell = "sell" #get rid of this if going live
    giveaway = "give away"

class UserProductBase(CoreModel):
    size: Optional[str]
    comment: Optional[str]
    what_do: Optional[WhatDo] = "trade"
    price: Optional[float]

class UserProductCreate(UserProductBase):
    """
    The only field required to create a profile is the users id
    """
    user_id: int
    product_id: int

class UserProductUpdate(UserProductBase):
    pass

class UserProductInDB(DateTimeModelMixin, UserProductBase):
    class Config:
        orm_mode = True

class UserProductPublic(UserProductInDB):
    user: Optional(UserPublic)
    product: Optional(ProductPublic)

    class Config:
        orm_mode = True