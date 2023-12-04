from main.const import INFURA_API_KEY, INFURA_SECRET_KEY
from requests.auth import HTTPBasicAuth
import requests
import logging
import json

logger = logging.getLogger()


def retrieve_proposal_text_from_ipfs(ipfs_hash: str):
    parsed_hash = ipfs_hash.split(":")[-1]
    url = f"https://ipfs.infura.io:5001/api/v0/cat?arg={parsed_hash}"
    try:
        response = requests.post(
            url,
            auth=HTTPBasicAuth(INFURA_API_KEY, INFURA_SECRET_KEY),
            timeout=20,
        )
    except requests.exceptions.ReadTimeout as e:
        logger.warning(f"IPFS retrieval failed due to timeout: {e}")
        return ""
    if response:
        data = json.loads(response.text)
        return data["text"]
    return ""
