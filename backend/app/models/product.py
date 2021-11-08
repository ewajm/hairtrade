from enum import Enum
from typing import Optional
from app.models.core import CoreModel
from app.models.core import IDModelMixin

class ProductType(str,Enum):
    dunno = "idk, a bottle"
    cream = "cream"
    spray = "spray"
    mousse = "mousse"
    gel = "gel"
    oil = "oil"
    shampoo = "shampoo"
    conditioner = "conditioner"
    mask = "mask"

class WhatDo(str, Enum):
    trade = "trade"
    sell = "sell" #get rid of this if going live
    giveaway = "give away"

class ProductBase(CoreModel):
    product_name: Optional[str]
    brand: Optional[str]
    description: Optional[str]
    type: Optional[ProductType] = "idk, a bottle"
    what_do: Optional[WhatDo] = "trade"
    price: Optional[float]

class ProductCreate(ProductBase):
    product_name: str
    type: ProductType

class ProductUpdate(ProductBase):
    what_do: Optional[WhatDo]
    type: Optional[ProductType]

class ProductInDB(IDModelMixin,ProductBase):
    product_name: str
    type: ProductType
    what_do: WhatDo

class ProductPublic(IDModelMixin,ProductBase):
    pass
