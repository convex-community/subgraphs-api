from typing import List
from models.convex.revenue import (
    ConvexRevenueSnapshotSchema,
    ConvexRevenueSnapshot,
    ConvexCumulativeRevenue,
    ConvexCumulativeRevenueSchema,
)
from tasks.queries.graph import grt_convex_pools_query
from celery.utils.log import get_task_logger
from main import db

logger = get_task_logger(__name__)

GRAPH_CONVEX_REVENUE_SNAPSHOTS_QUERY = """
{ dailyRevenueSnapshots(first: 1000 orderBy: timestamp orderDirection: desc) {
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
  otherRevenue
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
    totalOtherRevenue
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
    return ConvexRevenueSnapshotSchema(many=True, session=db.session).load(
        pools
    )


def get_convex_cumulative_revenue() -> ConvexCumulativeRevenue:
    logger.info(f"Querying Convex Cumulative Revenue")
    data = grt_convex_pools_query(
        GRAPH_CONVEX_CUMULATIVE_REVENUE_SNAPSHOTS_QUERY
    )
    revenue = []
    if data is not None and "platforms" in data:
        revenue = data["platforms"]
    if revenue:
        revenue = revenue[0]  # type: ignore
        revenue["id"] = "platform_rev"  # type: ignore
    return ConvexCumulativeRevenueSchema(session=db.session).load(revenue)
