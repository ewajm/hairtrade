from sqlalchemy import *
from datetime import datetime

metadata_obj = MetaData()

def mixin_factory():
    return (Column("created_at", TIMESTAMP, default=datetime.utcnow, nullable=False),\
        Column("updated_at", TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False))

products = Table("products", 
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("product_name", Text, nullable=False,index=True),
    Column("brand", Text, nullable=True),
    Column("description", Text, nullable=True),
    Column("type", Text, nullable=False, server_default="idk, a bottle"),
    Column("what_do", Text, nullable=False, server_default="trade"),
    Column("price", Numeric(10,2), nullable=True),
    *mixin_factory()
)

users = Table("users", 
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("username", Text, unique=True, nullable=False, index=True),        
    Column("email", Text, unique=True, nullable=False, index=True),
    Column("email_verified", Boolean, nullable=False, server_default="False"),
    Column("salt", Text, nullable=False),
    Column("password", Text, nullable=False),
    Column("is_active", Boolean(), nullable=False, server_default="True"),
    Column("is_superuser", Boolean(), nullable=False, server_default="False"),  
    *mixin_factory()
)


