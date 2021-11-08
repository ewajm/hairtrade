from sqlalchemy.sql.elements import literal_column
from app.db.repositories.base import BaseRepository
from app.models.product import ProductCreate, ProductUpdate, ProductInDB
from app.db.metadata import products

class ProductsRepository(BaseRepository):

    async def create_product(self,*,new_product:ProductCreate) -> ProductInDB:
        query = products.insert().values(new_product.dict()).returning(products.c.id, products.c.product_name, products.c.brand, products.c.description, 
        products.c.type, products.c.what_do, products.c.price)
        product = await self.db.fetch_one(query = query)

        return ProductInDB(**product)

    async def get_product_by_id(self, *, id:int) -> ProductInDB:
        query = products.select().where(products.c.id == id)
        product = await self.db.fetch_one(query = query)
        
        if not product:
            return None

        return ProductInDB(**product)
        