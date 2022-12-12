"""added fields for stripe

Revision ID: 8b2f1bc0dede
Revises: 9c736770cf71
Create Date: 2022-07-08 14:22:18.086429

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8b2f1bc0dede'
down_revision = '9c736770cf71'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('subscription_id', sa.String(length=60), nullable=True))
    op.add_column('users', sa.Column('customer_id', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'customer_id')
    op.drop_column('users', 'subscription_id')
    # ### end Alembic commands ###