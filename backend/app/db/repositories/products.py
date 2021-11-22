from typing import List
from fastapi.exceptions import HTTPException

from starlette.status import HTTP_400_BAD_REQUEST
from app.db.repositories.base import BaseRepository
from app.models.product import ProductCreate, ProductUpdate
from app.db.metadata import Product

class ProductsRepository(BaseRepository):

    def create_product(self,new_product:ProductCreate):
        db_product = Product(**new_product.dict())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def get_product_by_id(self, *, id:int):
        product = self.db.query(Product).filter(Product.id == id).first()
        
        if not product:
            return None

        return product
        
    def get_all_products(self):
        return self.db.query(Product).all()

    def update_product(self, *, id:int, product_update:ProductUpdate):
        target_product = self.get_product_by_id(id=id)
        if not target_product:
            return None

        update_performed = False

        for var,value in vars(product_update).items():
            print(str(var) + str(value))
            if value or str(value) == 'False':
                setattr(target_product, var, value)
                update_performed = True 
        
        
        if update_performed == False:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, 
                detail="No valid update parameters. No update performed",
            )

        try:
            self.db.add(target_product)
            self.db.commit()
            self.db.refresh(target_product)
            return target_product
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, 
                detail="Invalid update params.",                
            )

    def delete_product_by_id(self, *, id:int) -> int:
        target_product = self.get_product_by_id(id=id)
        if not target_product:
            return None

        deleted_id = target_product.id
        self.db.delete(target_product)
        self.db.commit()

        return deleted_id