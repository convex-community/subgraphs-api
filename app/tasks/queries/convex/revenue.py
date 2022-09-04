from typing import List
from models.convex.revenue import (
    ConvexRevenueSnapshotSchema,
    ConvexRevenueSnapshot,
)
from tasks.queries.graph import grt_convex_pools_query
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

GRAPH_CONVEX_REVENUE_SNAPSHOTS_QUERY = """
{ revenueWeeklySnapshots(first: 1000) {
  id
  crvRevenueToCallersAmount
  crvRevenueToPlatformAmount
  crvRevenueToCvxStakersAmount
  crvRevenueToLpProvidersAmount
  crvRevenueToCvxCrvStakersAmount
  totalCrvRevenue
  crvRevenueToCallersAmountCumulative
  crvRevenueToPlatformAmountCumulative
  crvRevenueToCvxStakersAmountCumulative
  crvRevenueToLpProvidersAmountCumulative
  crvRevenueToCvxCrvStakersAmountCumulative
  totalCrvRevenueCumulative
  crvPrice
  timestamp
}}
"""


def get_convex_revenue_snapshots() -> List[ConvexRevenueSnapshot]:
    logger.info(f"Querying Convex Revenue Snapshots")
    data = grt_convex_pools_query(GRAPH_CONVEX_REVENUE_SNAPSHOTS_QUERY)
    if data is None:
        return []
    pools = data.get("revenueWeeklySnapshots", [])
    return ConvexRevenueSnapshotSchema(many=True).load(pools)
