from main.common.subgraph_query import grt_query
from main.const import CURVE_DAO
from models.curve.dao import (
    DaoProposal,
    DaoProposalSchema,
    DaoDetailedProposalSchema,
    DaoDetailedProposal,
    UserLock,
    UserLockSchema,
    UserBalance,
    UserBalanceSchema,
    DaoVote,
    DaoVoteSchema,
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
    votes(first: 1000) {
      tx
      voteId
      voter
      supports
      stake
    }
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
        proposal,
        unknown=EXCLUDE,
    )


def get_user_locks(user: str) -> List[UserLock]:
    query_template = """
  {
    users(where: {id: "%s"}) {
      locks(orderBy: timestamp, orderDirection: asc) {
        value
        lockStart
        unlockTime
        type
        totalLocked
        timestamp
      }
    }
  }
    """
    query = query_template % user
    query_res = _query(query, "users")
    if len(query_res) == 0 or "locks" not in query_res[0]:
        return []
    return UserLockSchema(many=True).load(
        query_res[0]["locks"],
        unknown=EXCLUDE,
    )


def get_user_balance(user: str) -> List[UserBalance]:
    query_template = """
{
  userBalances(where: {user: "%s"}) {
    startTx
    crvLocked
    lockStart
    unlockTime
  }
}
    """
    query = query_template % user
    query_res = _query(query, "userBalances")
    return UserBalanceSchema(many=True).load(
        query_res,
        unknown=EXCLUDE,
    )


def get_user_votes(user: str) -> List[DaoVote]:
    # TODO: add timestamps / order by timestamp
    query_template = """
  {
    votes(first: 1000 where: {voter: "%s"} orderBy: stake, orderDirection: asc) {
      tx
      voteId
      voter
      supports
      stake
    }
  }
    """
    query = query_template % user
    query_res = _query(query, "votes")
    return DaoVoteSchema(many=True).load(
        query_res,
        unknown=EXCLUDE,
    )
