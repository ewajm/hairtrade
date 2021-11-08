from sqlalchemy import *

metadata_obj = MetaData()

products = Table("products", 
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("product_name", Text, nullable=False,index=True),
    Column("brand", Text, nullable=True),
    Column("description", Text, nullable=True),
    Column("type", Text, nullable=False, server_default="idk, a bottle"),
    Column("what_do", Text, nullable=False, server_default="trade"),
    Column("price", Numeric(10,2), nullable=True),
)
