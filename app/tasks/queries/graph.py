import requests
import time
from typing import List, Mapping, Any, Optional
from celery.utils.log import get_task_logger
from app import celery

logger = get_task_logger(__name__)


def grt_query(chain: str, query: str) -> Optional[Mapping[str, List[Mapping[str, Any]]]]:
    for i in range(3):
        endpoint_mapping = celery.conf.get("SUBGRAPHS")
        endpoint = endpoint_mapping.get(chain, None)
        if endpoint is None:
            logger.warning(f"Unable to find an endpoint for chain {chain}")
            return None
        r = requests.post(endpoint, json={'query': query})
        try:
            return r.json()['data']
        except (requests.exceptions.RequestsJSONDecodeError, requests.exceptions.ConnectionError):
            logger.error(f"Failed at fulfilling request {query} for {chain}, retrying (f{i}/3)")
            time.sleep(60)
            continue
