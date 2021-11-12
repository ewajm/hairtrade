from typing import Callable, Type
from fastapi import Depends
from sqlalchemy.orm import session

from app.db.repositories.base import BaseRepository
from app.db.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_repository(Repo_type: Type[BaseRepository]) -> Callable:
    def get_repo(db: session.Session = Depends(get_db)) -> Type[BaseRepository]:
        return Repo_type(db)

    return get_repo

