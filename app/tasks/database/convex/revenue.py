from models.convex.revenue import (
    ConvexRevenueSnapshotSchema,
    ConvexRevenueSnapshot,
)
from tasks.database.client import get_container
from typing import List

CONTAINER_NAME = "ConvexPlatformRevenue"


def update_convex_revenue_snapshots(pools: List[ConvexRevenueSnapshot]):
    container = get_container(CONTAINER_NAME)
    for pool in pools:
        container.upsert_item(ConvexRevenueSnapshotSchema().dump(pool))
