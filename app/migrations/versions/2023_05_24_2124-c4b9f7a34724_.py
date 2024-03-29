"""empty message

Revision ID: c4b9f7a34724
Revises: 2fe166270eba
Create Date: 2023-05-24 21:24:11.029955

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c4b9f7a34724"
down_revision = "2fe166270eba"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("convex_pool_snapshot", schema=None) as batch_op:
        batch_op.alter_column(
            "withdrawalCount",
            existing_type=sa.INTEGER(),
            type_=sa.BigInteger(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "withdrawalVolume",
            existing_type=sa.INTEGER(),
            type_=sa.BigInteger(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "lpTokenBalance",
            existing_type=sa.INTEGER(),
            type_=sa.BigInteger(),
            existing_nullable=True,
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("convex_pool_snapshot", schema=None) as batch_op:
        batch_op.alter_column(
            "lpTokenBalance",
            existing_type=sa.BigInteger(),
            type_=sa.INTEGER(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "withdrawalVolume",
            existing_type=sa.BigInteger(),
            type_=sa.INTEGER(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "withdrawalCount",
            existing_type=sa.BigInteger(),
            type_=sa.INTEGER(),
            existing_nullable=True,
        )

    # ### end Alembic commands ###
