from main.common.grt_query import grt_query
from main.const import CURVE_DAO
from models.curve.dao import DaoProposal, DaoProposalSchema
from flask import current_app
from typing import List
from marshmallow import EXCLUDE


def get_all_proposals() -> List[DaoProposal]:
    query = """
{
  proposals(first: 1000) {
    voteId
    voteType
    creator
    startDate
    snapshotBlock
    ipfsMetadata
    metadata
    votesFor
    votesAgainst
    voteCount
    supportRequired
    executed
  }
}
    """
    subgraph_endpoint = current_app.config["SUBGRAPHS"][CURVE_DAO]
    subgraph_data = grt_query(subgraph_endpoint, query)
    subgraph_data = (
        subgraph_data["proposals"] if "proposals" in subgraph_data else []
    )
    return DaoProposalSchema(many=True).load(
        subgraph_data,
        unknown=EXCLUDE,
    )
