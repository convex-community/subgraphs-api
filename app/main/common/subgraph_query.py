import requests
import time
from typing import List, Mapping, Any, Optional

import requests.exceptions
from celery.utils.log import get_task_logger

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
