from fastapi.exceptions import HTTPException
from starlette import status
from starlette.status import HTTP_400_BAD_REQUEST
from app.api.routes import items
from app.db.metadata import Item, User
from app.db.repositories.base import BaseRepository
from app.models import item
from app.models.item import ItemCreate, ItemUpdate
from app.models.user import UserInDB


class ItemRepository(BaseRepository):
    def create_item(self, *, item_create: ItemCreate, user_id:int):
        created_item = Item(**item_create.dict(), user_id=user_id)
        self.db.add(created_item)
        self.db.commit()
        self.db.refresh(created_item)
        return created_item

    def get_item_by_id(self,*,id:int):
        item = self.db.query(Item).filter(Item.id == id).first()
        if not item:
            return None

        return item

    def get_items_by_user_id(self, *, user_id:int):
        items = self.db.query(Item).filter(Item.user_id == user_id).all()
        if not items:
            return None
        return items

    def get_items_by_product_id(self, *, product_id:int):
        items = self.db.query(Item).filter(Item.product_id == product_id).all()
        if not items:
            return None

        return items

    def get_items_product_id_and_user_id(self, *, product_id:int, user_id:int):
        items = self.db.query(Item).filter(Item.product_id==product_id, Item.user_id == user_id).all()
        if not items:
            return None
        return items

    def get_all_items(self):
        return self.db.query(Item).all()

    def delete_item_by_id(self,*,id:int, requesting_user_id:UserInDB):
        target_item = self.get_item_by_id(id = id)
        if not target_item:
            return None

        if target_item.user_id != requesting_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail = "Users can only delete products they created."
            )

        deleted_id = target_item.id
        self.db.delete(target_item)
        self.db.commit()
        return deleted_id

    def update_item(self,*, id:int, item_update: ItemUpdate, requesting_user_id:int):
        target_item = self.get_item_by_id(id=id)
        if not target_item:
            return None
        
        if requesting_user_id != target_item.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Users are only able to udpate items that they created"
            )

        update_performed = False

        for var,value in vars(item_update).items():
            if value or str(value) == 'False':
                setattr(target_item, var, value)
                update_performed = True

        if update_performed == False:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="No valid update parameters. No update performed",
            )

        try:
            self.db.add(target_item)
            self.db.commit()
            self.db.refresh(target_item)
            return target_item
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, 
                detail="Invalid update params.",                
            )