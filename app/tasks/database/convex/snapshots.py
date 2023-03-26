from models.convex.snapshot import ConvexPoolSnapshot, ConvexPoolSnapshotSchema
from tasks.database.client import get_container
from typing import List
import math
import logging

logger = logging.getLogger(__name__)
CONTAINER_NAME = "ConvexPoolSnapshots"


def update_convex_pool_snapshots(pools: List[ConvexPoolSnapshot]):
    container = get_container(CONTAINER_NAME)
    for pool in pools:
        base_apr = pool["baseApr"] if "baseApr" in pool else None  # type: ignore
        if base_apr is None or math.isnan(base_apr) or math.isinf(base_apr):
            logger.error(f"Invalid or inexistant value for baseApr in {pool}")
            continue
        container.upsert_item(ConvexPoolSnapshotSchema().dump(pool))
