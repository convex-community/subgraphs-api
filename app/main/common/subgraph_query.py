import requests
import time
from typing import List, Mapping, Any, Optional

import requests.exceptions
from flask import current_app


def grt_query(
    endpoint: str, query: str
) -> Optional[Mapping[str, List[Mapping[str, Any]]]]:
    for i in range(3):
        r = requests.post(endpoint, json={"query": query}, timeout=600)
        try:
            return r.json().get("data", None)
        except (
            requests.exceptions.JSONDecodeError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ):
            current_app.logger.error(
                f"Failed at fulfilling request {query} for {endpoint}, retrying ({i}/3)"
            )
            time.sleep(60)
            continue
    return None
