"""name

Revision ID: 62a974e0630d
Revises: d5517a741ee4
Create Date: 2022-11-08 10:16:27.161237

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '62a974e0630d'
down_revision = 'd5517a741ee4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('session', 'user_id',
               existing_type=postgresql.UUID(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('session', 'user_id',
               existing_type=postgresql.UUID(),
               nullable=True)
    # ### end Alembic commands ###
