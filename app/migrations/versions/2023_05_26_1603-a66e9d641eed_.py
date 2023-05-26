"""empty message

Revision ID: a66e9d641eed
Revises: f0e2060cec74
Create Date: 2023-05-26 16:03:53.546393

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a66e9d641eed"
down_revision = "f0e2060cec74"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "curve_pool",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("symbol", sa.String(), nullable=True),
        sa.Column("chain", sa.String(), nullable=True),
        sa.Column("lpToken", sa.String(), nullable=True),
        sa.Column("coins", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("coinNames", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("isV2", sa.Boolean(), nullable=True),
        sa.Column("cumulativeVolumeUSD", sa.Float(), nullable=True),
        sa.Column("cumulativeFeesUSD", sa.Float(), nullable=True),
        sa.Column("virtualPrice", sa.Float(), nullable=True),
        sa.Column("baseApr", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "curve_pool_snapshot",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("pool", sa.String(), nullable=True),
        sa.Column("chain", sa.String(), nullable=True),
        sa.Column("virtualPrice", sa.Float(), nullable=True),
        sa.Column("A", sa.Integer(), nullable=True),
        sa.Column("lpPriceUSD", sa.Float(), nullable=True),
        sa.Column("tvl", sa.Float(), nullable=True),
        sa.Column("fee", sa.Float(), nullable=True),
        sa.Column("adminFee", sa.Float(), nullable=True),
        sa.Column("totalDailyFeesUSD", sa.Float(), nullable=True),
        sa.Column("reserves", postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column(
            "normalizedReserves", postgresql.ARRAY(sa.Integer()), nullable=True
        ),
        sa.Column("reservesUSD", postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column("volume", sa.Float(), nullable=True),
        sa.Column("volumeUSD", sa.Float(), nullable=True),
        sa.Column("baseApr", sa.Float(), nullable=True),
        sa.Column("rebaseApr", sa.Float(), nullable=True),
        sa.Column("timestamp", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("curve_pool_snapshot")
    op.drop_table("curve_pool")
    # ### end Alembic commands ###