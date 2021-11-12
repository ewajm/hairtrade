from sqlalchemy import *
from sqlalchemy.ext.declarative import declared_attr
from .database import Base

class BaseColumn(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column('created_at', TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column('updated_at', TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.current_timestamp())

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Product(BaseColumn, Base):
    product_name = Column(Text, nullable=False,index=True)
    brand = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    type = Column(Text, nullable=False, server_default="idk, a bottle")
    what_do = Column(Text, nullable=False, server_default="trade")
    price = Column(Numeric(10,2), nullable=True)

class User(BaseColumn, Base):
    username = Column(Text, unique=True, nullable=False, index=True)      
    email = Column(Text, unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, nullable=False, server_default="False")
    salt = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    is_active = Column(Boolean(), nullable=False, server_default="True")
    is_superuser = Column(Boolean(), nullable=False, server_default="False") 

