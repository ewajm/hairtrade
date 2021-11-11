from typing import List
from fastapi.exceptions import HTTPException

from sqlalchemy.sql.sqltypes import Integer
from starlette.status import HTTP_400_BAD_REQUEST
from app.db.repositories.base import BaseRepository
from app.models.product import ProductCreate, ProductUpdate, Product
from app.db.metadata import products

class ProductsRepository(BaseRepository):

    async def create_product(self,*,new_product:ProductCreate) -> Product:
        query = products.insert().values(new_product.dict()).returning(products.c.id, products.c.product_name, products.c.brand, products.c.description, 
        products.c.type, products.c.what_do, products.c.price)
        product = await self.db.fetch_one(query = query)

        return Product(**product)

    async def get_product_by_id(self, *, id:int) -> Product:
        query = products.select().where(products.c.id == id)
        product = await self.db.fetch_one(query = query)
        
        if not product:
            return None

        return Product(**product)
        
    async def get_all_products(self) -> List[Product]:
        query = products.select()
        product_list = await self.db.fetch_all(query=query)
        return [Product(**p) for p in product_list]

    async def update_product(self, *, id:int, product_update:ProductUpdate) -> Product:
        target_product = await self.get_product_by_id(id=id)
        if not target_product:
            return None

        product_update_params = target_product.copy(
            update=product_update.dict(exclude_unset=True),
        )

        if product_update_params.type is None or product_update_params.what_do is None:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, 
                detail="Invalid cleaning type. Cannot be None.",
            )

        query = products.update().where(products.c.id == id).values(product_update_params.dict()).\
            returning(products.c.id, products.c.product_name, products.c.brand, products.c.description, products.c.type, products.c.what_do, products.c.price)

        try:
            product = await self.db.fetch_one(query = query)
            return Product(**product)
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, 
                detail="Invalid update params.",                
            )

    async def delete_product_by_id(self, *, id:int) -> int:
        target_product = await self.get_product_by_id(id=id)
        if not target_product:
            return None
        
        query = products.delete().where(products.c.id==id).returning(products.c.id)

        deleted_id = await self.db.execute(query = query)

        return deleted_id