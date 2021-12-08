from enum import Enum
from typing import Optional
from app.models.core import CoreModel
from app.models.core import IDModelMixin
from app.models.core import DateTimeModelMixin

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


class ProductBase(CoreModel):
    product_name: Optional[str]
    brand: Optional[str]
    description: Optional[str]
    type: Optional[ProductType] = "idk, a bottle"
    price: Optional[float]

class ProductCreate(ProductBase):
    product_name: str
    type: ProductType

class ProductUpdate(ProductBase):
    type: Optional[ProductType]

class ProductInDB(IDModelMixin,DateTimeModelMixin, ProductBase):
    product_name: str
    type: ProductType

    class Config:
        orm_mode = True

class ProductPublic(ProductInDB):
    type: ProductType
    
    class Config:
        orm_mod = True
