from dataclasses import dataclass
import marshmallow_dataclass
from typing import List


@dataclass
class ConvexPool:
    id: str
    name: str
    token: str
    lpToken: str
    swap: str
    gauge: str
    crvRewardsPool: str
    isV2: bool
    creationDate: int
    creationBlock: int
    tvl: float
    curveTvlRatio: float
    baseApr: float
    crvApr: float
    cvxApr: float
    extraRewardsApr: float
    extraRewards: List[str]


ConvexPoolSchema = marshmallow_dataclass.class_schema(ConvexPool)


@dataclass
class ConvexPoolName:
    id: str
    name: str


ConvexPoolNameSchema = marshmallow_dataclass.class_schema(ConvexPoolName)
