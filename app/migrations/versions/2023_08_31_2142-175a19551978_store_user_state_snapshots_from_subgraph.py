"""Store user state snapshots from subgraph

Revision ID: 175a19551978
Revises: 772eb03e01b2
Create Date: 2023-08-31 21:42:10.960114

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "175a19551978"
down_revision = "772eb03e01b2"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_state_snapshots",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user", sa.String(), nullable=True),
        sa.Column("marketId", sa.String(), nullable=True),
        sa.Column("collateral", sa.Float(), nullable=True),
        sa.Column("collateralUsd", sa.Float(), nullable=True),
        sa.Column("collateralUp", sa.Float(), nullable=True),
        sa.Column("depositedCollateral", sa.Float(), nullable=True),
        sa.Column("debt", sa.Float(), nullable=True),
        sa.Column("n", sa.Float(), nullable=True),
        sa.Column("n1", sa.Float(), nullable=True),
        sa.Column("n2", sa.Float(), nullable=True),
        sa.Column("health", sa.Float(), nullable=True),
        sa.Column("loss", sa.Float(), nullable=True),
        sa.Column("lossPct", sa.Float(), nullable=True),
        sa.Column("softLiq", sa.Boolean(), nullable=True),
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
    op.drop_table("user_state_snapshots")
    # ### end Alembic commands ###
