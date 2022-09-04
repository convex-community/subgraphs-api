import requests
import time
from typing import List, Mapping, Any, Optional

import requests.exceptions
from celery.utils.log import get_task_logger
from app import celery
from main.const import CURVE_POOLS, CONVEX_POOLS

logger = get_task_logger(__name__)


def grt_query(
    endpoint: str, query: str
) -> Optional[Mapping[str, List[Mapping[str, Any]]]]:
    for i in range(3):
        r = requests.post(endpoint, json={"query": query}, timeout=300)
        try:
            return r.json()["data"]
        except (
            requests.exceptions.JSONDecodeError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ):
            logger.error(
                f"Failed at fulfilling request {query} for {endpoint}, retrying ({i}/3)"
            )
            time.sleep(60)
            continue
    return None


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
