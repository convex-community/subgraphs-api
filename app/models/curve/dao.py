from dataclasses import dataclass
from typing import List

import marshmallow_dataclass
import strawberry
from flask_restx import fields

from utils import convert_marshmallow


@strawberry.type
@dataclass
class DaoProposal:
    voteId: int
    voteType: str
    creator: str
    startDate: int
    snapshotBlock: int
    ipfsMetadata: str
    metadata: str
    votesFor: str
    votesAgainst: str
    voteCount: int
    supportRequired: str
    minAcceptQuorum: str
    totalSupply: str
    executed: bool


DaoProposalSchema = marshmallow_dataclass.class_schema(DaoProposal)


@dataclass
class DaoVote:
    tx: str
    voteId: int
    voter: str
    supports: bool
    stake: int


DaoVoteSchema = marshmallow_dataclass.class_schema(DaoVote)


@dataclass
class DaoDetailedProposal(DaoProposal):
    tx: str
    creatorVotingPower: str
    script: str
    votes: List[DaoVote]


flask_restx_dao_vote = convert_marshmallow(DaoVote)
flask_restx_dao_proposal_details = convert_marshmallow(DaoProposal)

flask_restx_dao_proposal_details["tx"] = fields.String()
flask_restx_dao_proposal_details["creatorVotingPower"] = fields.Integer()
flask_restx_dao_proposal_details["script"] = fields.String()


DaoDetailedProposalSchema = marshmallow_dataclass.class_schema(
    DaoDetailedProposal
)


@dataclass
class UserLock:
    value: int
    lockStart: int
    unlockTime: int
    type: str
    totalLocked: str
    timestamp: int


UserLockSchema = marshmallow_dataclass.class_schema(UserLock)


@dataclass
class UserBalance:
    unlockTime: int
    lockStart: int
    crvLocked: str
    startTx: str


UserBalanceSchema = marshmallow_dataclass.class_schema(UserBalance)


@dataclass
class Gauge:
    address: str
    name: str
    type: int
    weight: str


GaugeSchema = marshmallow_dataclass.class_schema(Gauge)


@dataclass
class Emission:
    gauge: str
    pool: str
    crvAmount: float
    value: float
    timestamp: int


EmissionSchema = marshmallow_dataclass.class_schema(Emission)
