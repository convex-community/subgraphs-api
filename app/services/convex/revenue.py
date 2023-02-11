from models.convex.revenue import (
    ConvexCumulativeRevenueSchema,
    ConvexCumulativeRevenue,
    ConvexRevenueSnapshot,
    ConvexRevenueSnapshotSchema,
)
from services.query import query_db, get_container
from typing import List
from marshmallow import EXCLUDE
import pandas as pd

GROUPER_MAPPING = {"w": "W-TUE", "m": "M", "y": "A"}


def _exec_query(query: str, container: str) -> List:
    return query_db(get_container(container), query)


def get_platform_total_revenue() -> List[ConvexCumulativeRevenue]:
    query = f"SELECT c.totalCrvRevenueToLpProviders, c.totalCvxRevenueToLpProviders, c.totalFxsRevenueToLpProviders, c.totalCrvRevenueToCvxCrvStakers, c.totalCvxRevenueToCvxCrvStakers, c.totalThreeCrvRevenueToCvxCrvStakers, c.totalFxsRevenueToCvxFxsStakers, c.totalCrvRevenueToCvxStakers, c.totalFxsRevenueToCvxStakers, c.totalCrvRevenueToCallers, c.totalFxsRevenueToCallers, c.totalCrvRevenueToPlatform, c.totalFxsRevenueToPlatform, c.totalCrvRevenue, c.totalFxsRevenue, c.totalBribeRevenue FROM ConvexCumulativePlatformRevenue as c"
    res = _exec_query(query, "ConvexCumulativePlatformRevenue")
    return ConvexCumulativeRevenueSchema(many=True).load(res, unknown=EXCLUDE)


def get_platform_revenue_snapshots(
    groupby: str = "w",
) -> List[ConvexRevenueSnapshot]:
    query = f"SELECT c.id, c.crvRevenueToLpProvidersAmount, c.cvxRevenueToLpProvidersAmount, c.crvRevenueToCvxCrvStakersAmount, c.cvxRevenueToCvxCrvStakersAmount, c.threeCrvRevenueToCvxCrvStakersAmount, c.crvRevenueToCvxStakersAmount, c.crvRevenueToCallersAmount, c.crvRevenueToPlatformAmount, c.totalCrvRevenue, c.fxsRevenueToCvxStakersAmount, c.fxsRevenueToCvxFxsStakersAmount, c.fxsRevenueToLpProvidersAmount, c.fxsRevenueToCallersAmount, c.fxsRevenueToPlatformAmount, c.totalFxsRevenue, c.bribeRevenue, c.crvPrice, c.cvxPrice, c.fxsPrice, c.timestamp FROM ConvexPlatformRevenue as c ORDER BY c.timestamp DESC"
    res = _exec_query(query, "ConvexPlatformRevenue")
    if groupby != "d":
        df = pd.DataFrame(res)
        df["timestamp"] = pd.to_datetime(
            df["timestamp"], format="%m/%d/%y %I:%M%p"
        )
        df = df.groupby(
            pd.Grouper(key="timestamp", freq=GROUPER_MAPPING.get(groupby, "w"))
        )
        df.reset_index(inplace=True)
        df["timestamp"] = df["timestamp"].astype(int)
        df["id"] = df["timestamp"].astype(str)
        res = df.to_dict(orient="records")

    import logging

    logger = logging.getLogger()
    logger.error(res)
    return ConvexRevenueSnapshotSchema(many=True).load(res, unknown=EXCLUDE)
