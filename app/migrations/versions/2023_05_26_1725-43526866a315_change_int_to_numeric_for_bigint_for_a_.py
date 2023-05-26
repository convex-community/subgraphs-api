"""Change int to numeric for bigint for A param as well

Revision ID: 43526866a315
Revises: f2768134004f
Create Date: 2023-05-26 17:25:11.473691

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "43526866a315"
down_revision = "f2768134004f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("curve_pool_snapshot", schema=None) as batch_op:
        batch_op.alter_column(
            "A",
            existing_type=sa.INTEGER(),
            type_=sa.Numeric(),
            existing_nullable=True,
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("curve_pool_snapshot", schema=None) as batch_op:
        batch_op.alter_column(
            "A",
            existing_type=sa.Numeric(),
            type_=sa.INTEGER(),
            existing_nullable=True,
        )

    # ### end Alembic commands ###