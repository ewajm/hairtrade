
import os
from app.core.config import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_URL = f"{DATABASE_URL}_test" if os.environ.get("TESTING") else DATABASE_URL

engine = create_engine(
    DB_URL,pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()