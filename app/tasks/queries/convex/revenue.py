from typing import List, Mapping, Any, Optional
from models.convex.revenue import (
    ConvexRevenueSnapshotSchema,
    ConvexRevenueSnapshot,
    ConvexCumulativeRevenue,
    ConvexCumulativeRevenueSchema,
)
from tasks.queries.graph import grt_convex_pools_query
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

GRAPH_CONVEX_REVENUE_SNAPSHOTS_QUERY = """
{ dailyRevenueSnapshots(first: 1000) {
  id
  crvRevenueToLpProvidersAmount
  cvxRevenueToLpProvidersAmount
  crvRevenueToCvxCrvStakersAmount
  cvxRevenueToCvxCrvStakersAmount
  threeCrvRevenueToCvxCrvStakersAmount
  crvRevenueToCvxStakersAmount
  crvRevenueToCallersAmount
  crvRevenueToPlatformAmount
  totalCrvRevenue
  fxsRevenueToCvxStakersAmount
  fxsRevenueToCvxFxsStakersAmount
  fxsRevenueToLpProvidersAmount
  fxsRevenueToCallersAmount
  fxsRevenueToPlatformAmount
  totalFxsRevenue
  bribeRevenue
  cvxPrice
  crvPrice
  fxsPrice
  timestamp
}}
"""

GRAPH_CONVEX_CUMULATIVE_REVENUE_SNAPSHOTS_QUERY = """
{
  platforms {
    totalCrvRevenueToLpProviders
    totalCvxRevenueToLpProviders
    totalFxsRevenueToLpProviders
    totalCrvRevenueToCvxCrvStakers
    totalCvxRevenueToCvxCrvStakers
    totalThreeCrvRevenueToCvxCrvStakers
    totalFxsRevenueToCvxFxsStakers
    totalCrvRevenueToCvxStakers
    totalFxsRevenueToCvxStakers
    totalCrvRevenueToCallers
    totalFxsRevenueToCallers
    totalCrvRevenueToPlatform
    totalFxsRevenueToPlatform
    totalCrvRevenue
    totalFxsRevenue
    totalBribeRevenue
  }
}
"""


def get_convex_revenue_snapshots() -> List[ConvexRevenueSnapshot]:
    logger.info(f"Querying Convex Revenue Snapshots")
    data = grt_convex_pools_query(GRAPH_CONVEX_REVENUE_SNAPSHOTS_QUERY)
    if data is None:
        return []
    pools = data.get("dailyRevenueSnapshots", [])
    return ConvexRevenueSnapshotSchema(many=True).load(pools)


def get_convex_cumulative_revenue() -> List[ConvexCumulativeRevenue]:
    logger.info(f"Querying Convex Cumulative Revenue")
    data = grt_convex_pools_query(
        GRAPH_CONVEX_CUMULATIVE_REVENUE_SNAPSHOTS_QUERY
    )
    if data is None:
        return []
    pools = data.get("platform", [])
    return ConvexCumulativeRevenueSchema(many=True).load(pools)
