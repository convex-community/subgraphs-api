from models.convex.snapshot import ConvexPoolSnapshot, ConvexPoolSnapshotSchema
from tasks.database.client import get_container
from typing import List

CONTAINER_NAME = "ConvexPoolSnapshots"


def update_convex_pool_snapshots(pools: List[ConvexPoolSnapshot]):
    container = get_container(CONTAINER_NAME)
    for pool in pools:
        container.upsert_item(ConvexPoolSnapshotSchema().dump(pool))
