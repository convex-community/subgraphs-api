from models.curve.pool import CurvePool, CurvePoolSchema
from typing import List
from tasks.queries.graph import grt_query
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

GRAPH_CURVE_POOL_QUERY = """
{ pools(first: 1000) 
    {
        id
        address
        name
        symbol
        lpToken
        coins
        coinNames
        isV2
        cumulativeVolumeUSD
        cumulativeFeesUSD
        virtualPrice
        baseApr
    }
}
"""


def get_curve_pools(chain: str) -> List[CurvePool]:
    logger.info(f"Querying Curve pools for {chain}")
    data = grt_query(chain, GRAPH_CURVE_POOL_QUERY)
    if data is None or 'pools' not in data:
        logger.warning(f"Empty data returned for curve pool query on {chain}")
        return []
    # make ids chain-specific and add chain property for filtering
    pools = [{**d, "id": d['id'] + f'-{chain}', "chain": chain} for d in data['pools']]
    return CurvePoolSchema(many=True).load(pools)
