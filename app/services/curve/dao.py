from main import db
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
    Gauge,
    GaugeSchema,
    Emission,
    EmissionSchema,
    CurveDaoScript,
)
from typing import List, Mapping, Any, Optional, MutableMapping
from flask import current_app
from marshmallow import EXCLUDE
from services.modules.decode_proposal import parse_data
import logging

logger = logging.getLogger(__name__)


def dao_subgraph_query(query: str, envelope: str) -> List[Mapping[str, Any]]:
    subgraph_endpoint = current_app.config["SUBGRAPHS"][CURVE_DAO]
    subgraph_data = grt_query(subgraph_endpoint, query)
    if not subgraph_data:
        return [{}]
    proposal_data = subgraph_data.get(envelope, [])
    return proposal_data


def get_all_proposals() -> List[DaoProposal]:
    query = """
{
  proposals(first: 1000) {
  id
  voteId
  voteType
  creator {
    id
  }
  startDate
  snapshotBlock
  ipfsMetadata
  metadata
  votesFor
  votesAgainst
  voteCount
  supportRequired
  minAcceptQuorum
  totalSupply
  executed
  }
}
  """
    proposals = dao_subgraph_query(query, "proposals")
    proposals = [
        {
            **proposal,
            "creator": proposal["creator"]["id"],
        }
        for proposal in proposals
    ]
    return DaoProposalSchema(many=True).load(
        proposals,
        unknown=EXCLUDE,
    )


def get_proposal_details(
    vote_id: int, vote_type: str
) -> Optional[DaoDetailedProposal]:
    query_template = """
  {
    proposals(where: {voteId: "%s" voteType: %s}) {
    id
    tx
    voteId
    voteType
    creator {
        id
    }
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
      voter {
        id
      }
      supports
      stake
    }
    supportRequired
    minAcceptQuorum
    totalSupply
    executed
    script
    }
  }
    """
    query = query_template % (vote_id, vote_type)
    query_res = dao_subgraph_query(query, "proposals")
    if len(query_res) == 0 or "script" not in query_res[0]:
        return None
    proposal: MutableMapping[str, Any] = dict(query_res[0])
    proposal["creator"] = proposal["creator"]["id"]
    proposal["votes"] = [
        {**vote, "voter": vote["voter"]["id"]} for vote in proposal["votes"]
    ]
    entry = (
        db.session.query(CurveDaoScript).filter_by(id=proposal["id"]).first()
    )
    if entry:
        proposal["script"] = entry.decodedScript
    else:
        logger.warning(f"No DB entry found for proposal {proposal['id']}")
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
    query_res = dao_subgraph_query(query, "users")
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
    query_res = dao_subgraph_query(query, "userBalances")
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
      voter {
        id
      }
      supports
      stake
    }
  }
    """
    query = query_template % user
    query_res = dao_subgraph_query(query, "votes")
    query_res = [{**vote, "voter": vote["voter"]["id"]} for vote in query_res]
    return DaoVoteSchema(many=True).load(
        query_res,
        unknown=EXCLUDE,
    )


def get_user_proposals(user: str) -> List[DaoProposal]:
    query = """
{
  proposals(first: 1000 where: {creator: "%s"} orderBy: startDate) {
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
  totalSupply
  executed
  }
}
  """

    return DaoProposalSchema(many=True).load(
        dao_subgraph_query(query % user, "proposals"),
        unknown=EXCLUDE,
    )


def get_all_gauges() -> List[Gauge]:
    query = """
{
  gauges(first: 1000) {
  address
    name
    type {
      id
    }
    weight: weights(first: 1 orderBy:timestamp orderDirection:desc) {
      weight
    }
  }
}
  """
    gauge_data = dao_subgraph_query(query, "gauges")
    flattened_data = [
        {
            **gauge,
            "type": gauge["type"]["id"],
            "weight": gauge["weight"][0].get("weight", 0),
        }
        for gauge in gauge_data
    ]
    return GaugeSchema(many=True).load(
        flattened_data,
        unknown=EXCLUDE,
    )


def _get_emission_data(entity: str, param: str) -> List[Emission]:
    query_template = """
    {
      emissions (where: {%s: "%s"} orderBy:timestamp orderDirection:desc) {
        gauge {
          address
        }
        pool {
          id
        }
        crvAmount
        value
        timestamp
      }
    }
      """
    query = query_template % (entity, param)
    data = dao_subgraph_query(query, "emissions")
    flattened_data = [
        {
            **emission,
            "pool": emission["pool"]["id"],
            "gauge": emission["gauge"]["address"],
        }
        for emission in data
    ]
    return EmissionSchema(many=True).load(
        flattened_data,
        unknown=EXCLUDE,
    )


def get_emissions_by_gauge(gauge: str) -> List[Emission]:
    return _get_emission_data("gauge", gauge)


def get_emissions_by_pool(pool: str) -> List[Emission]:
    return _get_emission_data("pool", pool)
