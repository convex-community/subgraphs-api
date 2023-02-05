from models.convex.pool import ConvexPool, ConvexPoolSchema
from typing import List, Mapping, Any
import re
from models.convex.snapshot import ConvexPoolSnapshotSchema
from tasks.queries.graph import grt_convex_pools_query
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

GRAPH_CONVEX_POOL_SNAPSHOTS_QUERY = """
{
    pools(first: 1000) {
        snapshots(first: 1000){
            id
            poolid {
                id
                swap
            }
            poolName
            withdrawalCount
            withdrawalVolume
            withdrawalValue
            depositCount
            depositVolume
            depositValue
            lpTokenBalance
            lpTokenVirtualPrice
            lpTokenUSDPrice
            tvl
            curveTvlRatio
            baseApr
            crvApr
            cvxApr
            extraRewardsApr
            timestamp
            block
        }
    }
}
"""


def _flatten(
    data: Mapping[str, List[Mapping[str, Any]]], attribute: str
) -> List[Mapping[str, Any]]:
    pools = data.get("pools", [])
    return [
        {
            **snapshot,
            "id": re.sub(r"\W+", "", snapshot["id"]),
            "poolid": snapshot["poolid"]["id"],
            "swap": snapshot["poolid"]["swap"],
        }
        for pool_snapshots in pools
        for snapshot in pool_snapshots[attribute]
    ]


def get_convex_pool_snapshots() -> List[ConvexPool]:
    logger.info(f"Querying Convex Pool Snapshots")
    data = grt_convex_pools_query(GRAPH_CONVEX_POOL_SNAPSHOTS_QUERY)
    if data is None:
        return []
    pools = _flatten(data, "snapshots")
    return ConvexPoolSnapshotSchema(many=True).load(pools)
