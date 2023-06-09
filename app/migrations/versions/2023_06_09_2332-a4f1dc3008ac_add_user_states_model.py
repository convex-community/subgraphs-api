"""Add user states model

Revision ID: a4f1dc3008ac
Revises: c81e95c5a297
Create Date: 2023-06-09 23:32:52.482594

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a4f1dc3008ac"
down_revision = "c81e95c5a297"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_states",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("marketId", sa.String(), nullable=True),
        sa.Column("collateral", sa.Numeric(), nullable=True),
        sa.Column("collateralUsd", sa.Numeric(), nullable=True),
        sa.Column("stableCoin", sa.Numeric(), nullable=True),
        sa.Column("debt", sa.Numeric(), nullable=True),
        sa.Column("N", sa.Numeric(), nullable=True),
        sa.Column("health", sa.Numeric(), nullable=True),
        sa.Column("timestamp", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["marketId"],
            ["market.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_states")
    # ### end Alembic commands ###