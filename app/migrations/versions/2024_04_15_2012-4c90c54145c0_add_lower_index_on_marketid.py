"""Add lower index on marketId

Revision ID: 4c90c54145c0
Revises: c96dc1fbed05
Create Date: 2024-04-15 20:12:39.802645

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c90c54145c0'
down_revision = 'c96dc1fbed05'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE INDEX idx_user_states_marketid_lower ON user_states (LOWER(marketId));")
    op.execute("CREATE INDEX idx_user_state_snapshots_marketid_lower ON user_state_snapshots (LOWER(marketId));")
    op.execute("CREATE INDEX idx_snapshot_marketid_lower ON snapshot (LOWER(marketId));")


def downgrade():
    op.execute("DROP INDEX idx_user_states_marketid_lower;")
    op.execute("DROP INDEX idx_user_state_snapshots_marketid_lower;")
    op.execute("DROP INDEX idx_snapshot_marketid_lower;")
