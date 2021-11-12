from databases import Database
from sqlalchemy.orm.session import Session

class BaseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db