
from app.core.config import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app import settings

try:
    settings.db_url
except AttributeError:
    settings.init()
    settings.db_url = DATABASE_URL

engine = create_engine(
    settings.db_url,pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()