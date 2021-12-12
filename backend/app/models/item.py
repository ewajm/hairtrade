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

class ItemBase(CoreModel):
    size: Optional[Size] = "regular"
    comment: Optional[str]
    what_do: Optional[WhatDo] = "trade"
    price: Optional[float]

class ItemCreate(ItemBase):
    user_id: int
    product_id: int
    what_do:WhatDo = "trade"

class ItemUpdate(ItemBase):
    pass

class ItemInDB(ItemBase):
    user_id: int
    product_id: int

    class Config:
        orm_mode = True

class ItemPublicByUser(ItemInDB):
    product: "Optional[ProductPublic]"

    class Config:
        orm_mode = True

class ItemPublicByProduct(ItemInDB):
    user: "Optional[UserPublic]"

    class Config:
        orm_mode = True

from app.models.product import ProductPublic
from app.models.user import UserPublic
ItemPublicByUser.update_forward_refs()
ItemPublicByProduct.update_forward_refs()