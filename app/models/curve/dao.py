from dataclasses import dataclass
import marshmallow_dataclass
import strawberry
from typing import List


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
    executed: bool


DaoProposalSchema = marshmallow_dataclass.class_schema(DaoProposal)
