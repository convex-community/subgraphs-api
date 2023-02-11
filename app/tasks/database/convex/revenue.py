from models.convex.revenue import (
    ConvexRevenueSnapshotSchema,
    ConvexRevenueSnapshot,
    ConvexCumulativeRevenue,
)
from tasks.database.client import get_container
from typing import List

CONTAINER_NAME = "ConvexPlatformRevenue"

CUMULATIVE_CONTAINER_NAME = "ConvexCumulativePlatformRevenue"


def update_convex_revenue_snapshots(pools: List[ConvexRevenueSnapshot]):
    container = get_container(CONTAINER_NAME)
    for pool in pools:
        container.upsert_item(ConvexRevenueSnapshotSchema().dump(pool))


def update_convex_cumulative_revenue(data: List[ConvexCumulativeRevenue]):
    if data:
        container = get_container(
            CUMULATIVE_CONTAINER_NAME, clear_existing=True
        )
        upsert_data = data[0].__dict__
        upsert_data["id"] = "ConvexTotalRevenue"
        container.upsert_item(upsert_data)
