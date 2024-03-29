from dataclasses import dataclass
from typing import List, Optional

import marshmallow
from marshmallow import Schema
from sqlalchemy import Column, String

import marshmallow_dataclass
from flask_restx import fields

from main import db
from utils import convert_schema


class CurveDaoScript(db.Model):
    __tablename__ = "curve_dao_proposal_scripts"

    id = Column(String, primary_key=True)
    script = Column(String)
    decodedScript = Column(String)


class CurveDaoMetadata(db.Model):
    __tablename__ = "curve_dao_proposal_metadata"

    id = Column(String, primary_key=True)
    ipfs_metadata = Column(String)


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


class DaoProposalSchema(Schema):
    voteId = marshmallow.fields.Int(required=True)
    voteType = marshmallow.fields.Str(required=True)
    creator = marshmallow.fields.Str(required=True)
    startDate = marshmallow.fields.Int(required=True)
    snapshotBlock = marshmallow.fields.Int(required=True)
    ipfsMetadata = marshmallow.fields.Str(required=True)
    metadata = marshmallow.fields.Str(allow_none=True)  # Allowing null for metadata
    votesFor = marshmallow.fields.Str(required=True)
    votesAgainst = marshmallow.fields.Str(required=True)
    voteCount = marshmallow.fields.Int(required=True)
    supportRequired = marshmallow.fields.Str(required=True)
    minAcceptQuorum = marshmallow.fields.Str(required=True)
    totalSupply = marshmallow.fields.Str(required=True)
    executed = marshmallow.fields.Boolean(required=True)

#DaoProposalSchema = marshmallow_dataclass.class_schema(DaoProposal)
#DaoProposalSchema.fields['metadata'] = fields.Str(allow_none=True)


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


flask_restx_dao_vote = convert_schema(DaoVote)
flask_restx_dao_proposal_details = convert_schema(DaoProposal)

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
