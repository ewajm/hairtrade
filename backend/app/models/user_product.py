from enum import Enum
from typing import Optional
from app.models.core import CoreModel, DateTimeModelMixin, IDModelMixin



class WhatDo(str, Enum):
    trade = "trade"
    sell = "sell" #get rid of this if going live
    giveaway = "give away"

class Size(str, Enum):
    sample = "sample"
    travel = "travel"
    regular = "regular"
    jumbo = "jumbo"

class UserProductBase(CoreModel):
    size: Optional[Size] = "regular"
    comment: Optional[str]
    what_do: Optional[WhatDo] = "trade"
    price: Optional[float]

class UserProductCreate(UserProductBase):
    user_id: int
    product_id: int
    what_do:WhatDo = "trade"

class UserProductUpdate(UserProductBase):
    pass

class UserProductInDB(UserProductBase):
    user_id: int
    product_id: int

    class Config:
        orm_mode = True

class UserProductPublic(UserProductInDB):
    # user: "Optional[UserPublic]"
    # product: "Optional[ProductPublic]"

    class Config:
        orm_mode = True

from app.models.product import ProductPublic
from app.models.user import UserPublic
UserProductPublic.update_forward_refs()