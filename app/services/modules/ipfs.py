from main.const import INFURA_API_KEY, INFURA_SECRET_KEY
from requests.auth import HTTPBasicAuth
import requests
import json


def retrieve_proposal_text_from_ipfs(ipfs_hash: str):
    parsed_hash = ipfs_hash.split(":")[-1]
    url = f"https://ipfs.infura.io:5001/api/v0/cat?arg={parsed_hash}"
    response = requests.post(
        url, auth=HTTPBasicAuth(INFURA_API_KEY, INFURA_SECRET_KEY), timeout=20
    )
    if response:
        data = json.loads(response.text)
        return data["text"]
    return ""
