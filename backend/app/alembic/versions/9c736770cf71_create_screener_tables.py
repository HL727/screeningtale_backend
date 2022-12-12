"""create screener tables

Revision ID: 9c736770cf71
Revises: 85b679f4d671
Create Date: 2022-06-21 09:54:39.556798

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9c736770cf71"
down_revision = "85b679f4d671"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "screener",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("criteria", sa.String(), nullable=False),
        sa.Column("creator_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_screener_id"), "screener", ["id"], unique=False)
    op.create_index(
        op.f("ix_screener_creator_id"), "screener", ["creator_id"], unique=False
    )
    # op.create_index(op.f("ix_screener_name"), "screener", ["name"], unique=False)


def downgrade() -> None:
    op.drop_table("screener")
