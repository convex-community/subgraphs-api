from main import db
from models.convex.pool import ConvexPool, ConvexPoolSchema
from typing import List
from tasks.queries.graph import grt_convex_pools_query
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

GRAPH_CONVEX_POOL_QUERY = """
{ pools(first: 1000)
    {
        id
        name
        token
        lpToken
        swap
        gauge
        crvRewardsPool
        isV2
        creationDate
        creationBlock
        tvl
        curveTvlRatio
        baseApr
        crvApr
        cvxApr
        extraRewardsApr
        extraRewards {
            contract
        }
    }
}
"""


def get_convex_pools() -> List[ConvexPool]:
    logger.info(f"Querying Convex Pools")
    data = grt_convex_pools_query(GRAPH_CONVEX_POOL_QUERY)
    if data is None or "pools" not in data:
        logger.warning(f"Empty data returned for convex pool query")
        return []
    # flatten extra rewards to list of contracts
    pools = [
        {**d, "extraRewards": [e["contract"] for e in d["extraRewards"]]}
        for d in data["pools"]
    ]
    return ConvexPoolSchema(many=True, session=db.session).load(pools)
