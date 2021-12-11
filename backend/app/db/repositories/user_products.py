from app.db.metadata import User, UserProduct
from app.db.repositories.base import BaseRepository
from app.models.user_product import UserProductCreate


class UserProductRepository(BaseRepository):
    def create_user_product(self, *, user_product_create: UserProductCreate):
        created_user_product = UserProduct(**user_product_create.dict())
        self.db.add(created_user_product)
        self.db.commit()
        self.db.refresh(created_user_product)
        return created_user_product

    def get_user_products_by_user_id(self, *, user_id:int):
        user_products = self.db.query(UserProduct).filter(UserProduct.user_id == user_id).all()
        if not user_products:
            return None

        return user_products

    def get_user_products_by_product_id(self, *, product_id:int):
        user_products = self.db.query(UserProduct).filter(UserProduct.product_id == product_id).all()
        if not user_products:
            return None

        return user_products

    def get_all_user_products(self):
        return self.db.query(UserProduct).all()