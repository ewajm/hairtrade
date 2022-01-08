from fastapi.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST
from app.db.metadata import Trade
from app.db.repositories.base import BaseRepository
from app.models.trade import TradeCreate, TradeUpdate


class TradeRepository(BaseRepository):
    def create_trade(self, *, trade_create: TradeCreate, user_id:int):
        created_trade = Trade(**trade_create.dict(), user_id=user_id)
        self.db.add(created_trade)
        self.db.commit()
        self.db.refresh(created_trade)
        return created_trade

    def get_trade_by_id(self,*,id:int):
        trade = self.db.query(Trade).filter(Trade.id == id).first()
        if not trade:
            return None

        return trade

    def get_trades_by_user_id(self, *, user_id:int):
        trades = self.db.query(Trade).filter(Trade.user_id == user_id).all()
        if not trades:
            return None
        return trades

    def get_trades_by_product_id(self, *, product_id:int):
        trades = self.db.query(Trade).filter(Trade.product_id == product_id).all()
        if not trades:
            return None

        return trades

    def get_trades_by_product_id_and_user_id(self, *, product_id:int, user_id:int):
        trades = self.db.query(Trade).filter(Trade.product_id==product_id, Trade.user_id == user_id).all()
        if not trades:
            return None
        return trades

    def get_all_trades(self):
        return self.db.query(Trade).all()

    def delete_trade_by_id(self,*,trade:Trade):
        deleted_id = trade.id
        self.db.delete(trade)
        self.db.commit()
        return deleted_id

    def update_trade(self,*, trade:Trade, trade_update: TradeUpdate):
        update_performed = False

        for var,value in vars(trade_update).items():
            if value or str(value) == 'False':
                setattr(trade, var, value)
                update_performed = True

        if update_performed == False:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="No valid update parameters. No update performed",
            )

        try:
            self.db.add(trade)
            self.db.commit()
            self.db.refresh(trade)
            return trade
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST, 
                detail="Invalid update params.",                
            )