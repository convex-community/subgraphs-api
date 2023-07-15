from typing import List, Mapping, Any, Optional

from app import celery
from main.const import CURVE_POOLS, CONVEX_POOLS, CRVUSD
from main.common.subgraph_query import grt_query
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def grt_curve_pools_query(
    chain: str, query: str
) -> Optional[Mapping[str, List[Mapping[str, Any]]]]:
    endpoint_mapping = celery.conf.get("SUBGRAPHS").get(CURVE_POOLS, {})
    endpoint = endpoint_mapping.get(chain, None)
    if endpoint is None:
        logger.warning(f"Unable to find an endpoint for {CURVE_POOLS} {chain}")
        return None
    return grt_query(endpoint, query)


def grt_convex_pools_query(
    query: str,
) -> Optional[Mapping[str, List[Mapping[str, Any]]]]:
    endpoint = celery.conf.get("SUBGRAPHS").get(CONVEX_POOLS, {})
    if endpoint is None:
        logger.warning(f"Unable to find an endpoint for {CONVEX_POOLS}")
        return None
    return grt_query(endpoint, query)


def grt_crvusd_query(
    query: str,
) -> Optional[Mapping[str, List[Mapping[str, Any]]]]:
    endpoint = celery.conf.get("SUBGRAPHS").get(CRVUSD, {})
    if endpoint is None:
        logger.warning(f"Unable to find an endpoint for {CRVUSD}")
        return None
    return grt_query(endpoint, query)
