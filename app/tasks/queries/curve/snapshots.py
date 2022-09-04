from models.curve.snapshot import CurvePoolSnapshot, CurvePoolSnapshotSchema
from typing import List, Mapping, Any
from tasks.queries.graph import grt_curve_pools_query
from celery.utils.log import get_task_logger
import pandas as pd

logger = get_task_logger(__name__)


GRAPH_CURVE_POOL_SNAPSHOT_QUERY = """
{ pools(first: 1000) {
  dailyPoolSnapshots(first: 1000 orderBy: timestamp orderDirection: desc) {
    id
    pool {
        id
    }
    virtualPrice
    lpPriceUSD
    tvl
    fee
    adminFee
    totalDailyFeesUSD
    reserves
    reservesUSD
    baseApr
    rebaseApr
    timestamp
  }
}
}
"""

GRAPH_CURVE_VOLUME_SNAPSHOT_QUERY = """
{ pools(first: 1000) {
  swapVolumeSnapshots(first: 1000 orderBy: timestamp orderDirection: desc where: {period: 86400}) {
    pool {
        id
    }
    volume
    volumeUSD
    timestamp
  }
}
}
"""


def _flatten(
    data: Mapping[str, List[Mapping[str, Any]]], attribute: str
) -> List[Mapping[str, Any]]:
    if "pools" not in data:
        return []
    return [
        {**snapshot, "pool": snapshot["pool"]["id"]}
        for pool_snapshots in data["pools"]
        for snapshot in pool_snapshots[attribute]
    ]


def get_curve_pool_standard_snapshots(chain: str) -> List[Mapping[str, Any]]:
    data = grt_curve_pools_query(chain, GRAPH_CURVE_POOL_SNAPSHOT_QUERY)
    if data is None:
        return []
    return _flatten(data, "dailyPoolSnapshots")


def get_curve_pool_volume_snapshots(chain: str) -> List[Mapping[str, Any]]:
    data = grt_curve_pools_query(chain, GRAPH_CURVE_VOLUME_SNAPSHOT_QUERY)
    if data is None:
        return []
    return _flatten(data, "swapVolumeSnapshots")


def get_curve_pool_snapshots(chain: str) -> List[CurvePoolSnapshot]:
    logger.info(f"Querying Curve pool snapshots for {chain}")
    pool_data = get_curve_pool_standard_snapshots(chain)
    vol_data = get_curve_pool_volume_snapshots(chain)
    if not pool_data or not vol_data:
        logger.warning(f"Empty data returned for curve pool query on {chain}")
        return []
    df = pd.merge(
        pd.DataFrame(pool_data),
        pd.DataFrame(vol_data),
        on=["pool", "timestamp"],
    )
    merged_data = df.to_dict(orient="records")
    snapshot_data = [
        {**d, "id": d["id"] + f"-{chain}", "chain": chain}  # type:ignore
        for d in merged_data
    ]
    return CurvePoolSnapshotSchema(many=True).load(snapshot_data)
