from app.api.routes import items
from app.db.metadata import Item, User
from app.db.repositories.base import BaseRepository
from app.models import item
from app.models.item import ItemCreate


class ItemRepository(BaseRepository):
    def create_item(self, *, item_create: ItemCreate):
        created_item = Item(**item_create.dict())
        self.db.add(created_item)
        self.db.commit()
        self.db.refresh(created_item)
        return created_item

    def get_items_by_user_id(self, *, user_id:int):
        items = self.db.query(Item).filter(Item.user_id == user_id).all()
        if not items:
            return None

        return items

    def get_user_products_by_product_id(self, *, product_id:int):
        items = self.db.query(Item).filter(Item.product_id == product_id).all()
        if not items:
            return None

        return items

    def get_all_items(self):
        return self.db.query(Item).all()