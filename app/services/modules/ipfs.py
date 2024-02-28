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


def fetch_from_public_gateway(ipfs_hash: str) -> str | None:
    parsed_hash = ipfs_hash.split(":")[-1]
    public_gateways = [
        "https://gateway.pinata.cloud/ipfs/",
        "https://fleek.ipfs.io/ipfs/",
        "https://cloudflare-ipfs.com/ipfs/",
    ]
    for gateway in public_gateways:
        url = gateway + parsed_hash
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return stringify_response(response)
            else:
                raise Exception(f"Failed to retrieve data, status code: {response.status_code}")
        except Exception as e:
            logger.debug(f"IPFS {gateway} retrieval failed: {e}")
    return None


def stringify_response(response) -> str:
    if "application/json" in response.headers.get("Content-Type", ""):
        data = response.json()
        return str(data.get("text", ""))
    else:
        data = response.text
        try:
            return str(json.loads(data).get("text", ""))
        except json.JSONDecodeError:
            return data

