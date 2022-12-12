"""Added market cap usd

Revision ID: bd5a839b05ca
Revises: 8b2f1bc0dede
Create Date: 2022-07-13 12:01:37.120107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bd5a839b05ca'
down_revision = '8b2f1bc0dede'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('historical', sa.Column('market_cap_usd', sa.REAL, nullable=True))
    op.add_column('screening_ticker', sa.Column('market_cap_usd', sa.REAL, nullable=True))


def downgrade() -> None:
    op.drop_column('historical', 'market_cap_usd')
    op.drop_column('screening_ticker', 'market_cap_usd')
