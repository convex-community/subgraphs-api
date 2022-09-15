from main.common.subgraph_query import grt_query
from main.const import CURVE_DAO
from models.curve.dao import (
    DaoProposal,
    DaoProposalSchema,
    DaoDetailedProposalSchema,
    DaoDetailedProposal,
)
from typing import List, Mapping, Any, Optional, MutableMapping
from flask import current_app
from marshmallow import EXCLUDE
from services.modules.decode_proposal import parse_data


def _query(query: str, envelope: str) -> List[Mapping[str, Any]]:
    subgraph_endpoint = current_app.config["SUBGRAPHS"][CURVE_DAO]
    subgraph_data = grt_query(subgraph_endpoint, query)
    if not subgraph_data:
        return [{}]
    proposal_data = (
        subgraph_data[envelope] if envelope in subgraph_data else []
    )
    return proposal_data


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
    minAcceptQuorum
    executed
  }
}
    """

    return DaoProposalSchema(many=True).load(
        _query(query, "proposals"),
        unknown=EXCLUDE,
    )


def get_proposal_details(
    vote_id: int, vote_type: str
) -> Optional[DaoDetailedProposal]:
    query_template = """
    {
      proposals(where: {voteId: "%s" voteType: %s}) {
        tx
        voteId
        voteType
        creator
        startDate
        snapshotBlock
        ipfsMetadata
        metadata
        votesFor
        creatorVotingPower
        votesAgainst
        voteCount
        supportRequired
        minAcceptQuorum
        executed
        script
      }
    }
        """
    query = query_template % (vote_id, vote_type)
    query_res = _query(query, "proposals")
    if len(query_res) == 0 or "script" not in query_res[0]:
        return None
    proposal: MutableMapping[str, Any] = dict(query_res[0])
    proposal["script"] = parse_data(proposal["script"])
    return DaoDetailedProposalSchema().load(
        query_res,
        unknown=EXCLUDE,
    )
