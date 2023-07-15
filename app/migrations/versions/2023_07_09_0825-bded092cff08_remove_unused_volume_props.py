"""Remove unused volume props

Revision ID: bded092cff08
Revises: c26e332c1ae4
Create Date: 2023-07-09 08:25:26.301579

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bded092cff08"
down_revision = "c26e332c1ae4"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("amm", schema=None) as batch_op:
        batch_op.drop_column("totalDepositVolume")
        batch_op.drop_column("totalVolume")

    with op.batch_alter_table("volumeSnapshot", schema=None) as batch_op:
        batch_op.drop_column("depositVolumeUsd")
        batch_op.drop_column("totalVolumeUsd")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("volumeSnapshot", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "totalVolumeUsd",
                sa.NUMERIC(),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "depositVolumeUsd",
                sa.NUMERIC(),
                autoincrement=False,
                nullable=True,
            )
        )

    with op.batch_alter_table("amm", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "totalVolume",
                sa.DOUBLE_PRECISION(precision=53),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "totalDepositVolume",
                sa.DOUBLE_PRECISION(precision=53),
                autoincrement=False,
                nullable=True,
            )
        )

    # ### end Alembic commands ###
