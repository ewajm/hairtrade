"""create_main_tables

Revision ID: bb5abaf49a1c
Revises: 
Create Date: 2021-11-04 02:41:06.265489

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = 'bb5abaf49a1c'
down_revision = None
branch_labels = None
depends_on = None

def create_cleanings_table() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.Text, nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("type", sa.Text, nullable=False, server_default="bottle"),
        sa.Column("what_do", sa.Text, nullable=False, server_default="trade"),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
    )

def upgrade() -> None:
    create_cleanings_table()


def downgrade() -> None:
    op.drop_table("cleanings")

