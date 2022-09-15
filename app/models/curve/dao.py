from dataclasses import dataclass
import marshmallow_dataclass
import strawberry


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


@strawberry.type
@dataclass
class DaoDetailedProposal(DaoProposal):
    tx: str
    creatorVotingPower: int
    script: str


DaoDetailedProposalSchema = marshmallow_dataclass.class_schema(
    DaoDetailedProposal
)
