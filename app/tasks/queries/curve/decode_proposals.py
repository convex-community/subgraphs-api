from main import db
from models.curve.dao import CurveDaoScript
from services.curve.dao import dao_subgraph_query
from services.modules.decode_proposal import parse_data_etherscan
import logging

logger = logging.getLogger(__name__)


def decode_proposals():
    query = """
    {
      proposals(first: 1000, orderBy: startDate orderDirection: desc) {
      id
      script
      }
    }
      """
    query_res = dao_subgraph_query(query, "proposals")
    for proposal in query_res:
        entry = (
            db.session.query(CurveDaoScript)
            .filter_by(id=proposal["id"])
            .first()
        )
        if entry:
            continue
        logging.info(f"Decoding script for proposal {proposal['id']}")
        decoded_script = parse_data_etherscan(proposal["script"])
        logging.info(f"Decoded script: {decoded_script}")
        prop = CurveDaoScript(
            id=proposal["id"],
            script=proposal["script"],
            decodedScript=decoded_script,
        )
        db.session.merge(prop)
    db.session.commit()
