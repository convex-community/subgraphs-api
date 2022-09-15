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
    votesFor: int
    votesAgainst: int
    voteCount: int
    supportRequired: int
    minAcceptQuorum: int
    executed: bool


DaoProposalSchema = marshmallow_dataclass.class_schema(DaoProposal)


@dataclass
class DaoVote:
    tx: str
    voter: str
    supports: bool
    stake: int


@dataclass
class DaoDetailedProposal(DaoProposal):
    tx: str
    creatorVotingPower: int
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
    totalLocked: int
    timestamp: int


UserLockSchema = marshmallow_dataclass.class_schema(UserLock)


@dataclass
class UserBalance:
    unlockTime: int
    lockStart: int
    crvLocked: int
    startTx: str


UserBalanceSchema = marshmallow_dataclass.class_schema(UserBalance)
