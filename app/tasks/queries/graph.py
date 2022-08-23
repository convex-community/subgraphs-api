import requests
from typing import List, Mapping, Any, Optional
from celery.utils.log import get_task_logger
from app import celery

logger = get_task_logger(__name__)


def grt_query(chain: str, query: str) -> Optional[Mapping[str, List[Mapping[str, Any]]]]:
    endpoint_mapping = celery.conf.get("SUBGRAPHS")
    endpoint = endpoint_mapping.get(chain, None)
    if endpoint is None:
        logger.warning(f"Unable to find an endpoint for chain {chain}")
        return None
    r = requests.post(endpoint, json={'query': query})
    return r.json()['data']
