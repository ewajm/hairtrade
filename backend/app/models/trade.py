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

class TradeBase(CoreModel):
    size: Optional[Size] = "regular"
    comment: Optional[str]
    what_do: Optional[WhatDo] = "trade"
    price: Optional[float]

class TradeCreate(TradeBase):
    product_id: int
    what_do:WhatDo = "trade"

class TradeUpdate(TradeBase):
    size: Optional[Size]
    what_do: Optional[WhatDo]

class TradeInDB(DateTimeModelMixin, IDModelMixin, TradeBase):
    user_id: int
    product_id: int

    class Config:
        orm_mode = True

class TradePublic(TradeInDB):
    product: "ProductInDB"
    user: "UserInDB"

    class Config:
        orm_mode = True

class TradePublicByUser(TradeInDB):
    product: "ProductInDB"

    class Config:
        orm_mode = True

class TradePublicByProduct(TradeInDB):
    user: "UserInDB"

    class Config:
        orm_mode = True

from app.models.product import ProductInDB
from app.models.user import UserInDB
TradePublicByUser.update_forward_refs()
TradePublicByProduct.update_forward_refs()
TradePublic.update_forward_refs()