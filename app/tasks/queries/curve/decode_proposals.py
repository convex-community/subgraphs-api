from main import db
from models.curve.dao import CurveDaoScript, CurveDaoMetadata
from services.curve.dao import dao_subgraph_query
from services.modules.decode_proposal import parse_data_etherscan
import logging

from services.modules.ipfs import retrieve_proposal_text_from_ipfs, fetch_from_public_gateway

logger = logging.getLogger(__name__)


def decode_proposals():
    query = """
    {
      proposals(first: 1000, orderBy: startDate orderDirection: desc) {
      id
      script
      metadata
      ipfsMetadata
      }
    }
      """
    query_res = dao_subgraph_query(query, "proposals")
    for proposal in query_res:
        # decode proposal data
        entry = (
            db.session.query(CurveDaoScript)
            .filter_by(id=proposal["id"])
            .first()
        )
        if not entry:
            logging.info(f"Decoding script for proposal {proposal['id']}")
            decoded_script = parse_data_etherscan(proposal["script"])
            logging.info(f"Decoded script: {decoded_script}")
            prop = CurveDaoScript(
                id=proposal["id"],
                script=proposal["script"],
                decodedScript=decoded_script,
            )
            db.session.merge(prop)

        # ensure metadata from IPFS
        if proposal["metadata"] != "":
            continue
        entry = (
            db.session.query(CurveDaoMetadata)
            .filter_by(id=proposal["id"])
            .first()
        )
        if entry and entry.ipfs_metadata != "":
            continue
        logging.info(
            f"Retrieving metadata for proposal {proposal['id']} ({proposal['ipfsMetadata']})"
        )
        if "ipfs:" not in proposal["ipfsMetadata"]:
            metadata = "No IPFS metadata"
        else:
            metadata = retrieve_proposal_text_from_ipfs(proposal["ipfsMetadata"])
        if metadata == "" or metadata is None:
            metadata = fetch_from_public_gateway(proposal["ipfsMetadata"])
        logging.info(f"Retrieved data: {metadata}")
        if metadata == "":
            logging.error("No metadata retrieved for the proposal")
            continue
        prop = CurveDaoMetadata(
            id=proposal["id"],
            ipfs_metadata=metadata,
        )
        db.session.merge(prop)
    db.session.commit()
