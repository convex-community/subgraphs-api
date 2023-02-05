from models.convex.snapshot import ConvexPoolSnapshot, ConvexPoolSnapshotSchema
from tasks.database.client import get_container
from typing import List
import math

CONTAINER_NAME = "ConvexPoolSnapshots"


def update_convex_pool_snapshots(pools: List[ConvexPoolSnapshot]):
    container = get_container(CONTAINER_NAME)
    for pool in pools:
        base_apr = pool.baseApr
        if math.isnan(base_apr) or math.isinf(base_apr):
            continue
        container.upsert_item(ConvexPoolSnapshotSchema().dump(pool))
