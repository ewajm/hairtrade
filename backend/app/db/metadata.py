from sqlalchemy import *
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
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
    users = relationship("Item", back_populates="product",
        cascade="all, delete",
        passive_deletes=True,)

class User(BaseColumn, Base):
    username = Column(Text, unique=True, nullable=False, index=True)      
    email = Column(Text, unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, nullable=False, server_default="False")
    salt = Column(Text, nullable=False)
    password = Column(Text, nullable=False)
    is_active = Column(Boolean(), nullable=False, server_default="True")
    is_superuser = Column(Boolean(), nullable=False, server_default="False") 
    profile = relationship(
        "Profile", back_populates="user",
        uselist=False,
        cascade="all, delete",
        passive_deletes=True,
    )
    products = relationship("Item", back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )

class Item(BaseColumn, Base):
    __tablename__='item'
    id = Column(Integer, primary_key=True, index=True, unique=True, autoincrement=True)
    user_id=Column(ForeignKey('user.id'), primary_key=True)
    user = relationship("User", back_populates="products")
    product_id = Column(ForeignKey('product.id'), primary_key=True)
    product = relationship("Product", back_populates="users")
    what_do = Column(Text, nullable=False, server_default="trade") 
    price = Column(Numeric(10,2), nullable=True) 
    comment = Column(Text,nullable=True)
    size = Column(Text,nullable=True)

#TODO add hair specific stuff like curl type, porosity etc. 
class Profile(BaseColumn, Base):
    id = Column(Integer, primary_key=True)
    full_name = Column(Text, nullable=True)
    phone_number = Column(Text, nullable=True)
    bio =  Column(Text, nullable=True, server_default=" ")
    image =  Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="profile")
    username = association_proxy("user", "username")
    email = association_proxy("user", "email")
