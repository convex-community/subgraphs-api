from models.convex.revenue import ConvexCumulativeRevenueSchema, \
    ConvexCumulativeRevenue, ConvexHistoricalRevenueSnapshotSchema, ConvexHistoricalRevenueSnapshot
from services.query import query_db, get_container
from typing import List
from marshmallow import EXCLUDE


def _exec_query(query: str) -> List:
    return query_db(get_container("ConvexPlatformRevenue"), query)


def get_platform_total_revenue() -> List[ConvexCumulativeRevenue]:
    query = f"SELECT TOP 1 c.crvRevenueToLpProvidersAmountCumulative, c.crvRevenueToCvxCrvStakersAmountCumulative, c.crvRevenueToCvxStakersAmountCumulative, c.crvRevenueToCallersAmountCumulative, c.crvRevenueToPlatformAmountCumulative, c.totalCrvRevenueCumulative, c.crvPrice FROM ConvexPoolSnapshots as c ORDER BY c.timestamp DESC"
    return ConvexCumulativeRevenueSchema(many=True).load(_exec_query(query), unknown=EXCLUDE)


def get_platform_revenue_snapshots() -> List[ConvexHistoricalRevenueSnapshot]:
    query = f"SELECT c.crvRevenueToLpProvidersAmount, c.crvRevenueToCvxCrvStakersAmount, c.crvRevenueToCvxStakersAmount, c.crvRevenueToCallersAmount, c.crvRevenueToPlatformAmount, c.crvPrice, c.timestamp FROM ConvexPoolSnapshots as c ORDER BY c.timestamp DESC"
    return ConvexHistoricalRevenueSnapshotSchema(many=True).load(_exec_query(query), unknown=EXCLUDE)
