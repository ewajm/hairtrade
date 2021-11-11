from sqlalchemy import *
from .database import Base

class BaseColumn(object):
    id = Column(Integer, primary_key=True, index=True)
    created = Column('created', DateTime(timezone=True), server_default=func.now())
    updated = Column('updated', DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp())

class Product(Base, BaseColumn):
    __tablename__ = "products" 

    product_name = Column(Text, nullable=False,index=True),
    brand = Column(Text, nullable=True),
    description = Column(Text, nullable=True),
    type = Column(Text, nullable=False, server_default="idk, a bottle"),
    what_do = Column(Text, nullable=False, server_default="trade"),
    price = Column(Numeric(10,2), nullable=True),

class User(Base, BaseColumn):
    __tablename__ = "users"
    username = Column(Text, unique=True, nullable=False, index=True),        
    email = Column(Text, unique=True, nullable=False, index=True),
    email_verified = Column(Boolean, nullable=False, server_default="False"),
    salt = Column(Text, nullable=False),
    password = Column(Text, nullable=False),
    is_active = Column(Boolean(), nullable=False, server_default="True"),
    is_superuser = Column(Boolean(), nullable=False, server_default="False"),  

