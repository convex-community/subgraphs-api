from dataclasses import dataclass
import marshmallow_dataclass
import strawberry
from typing import List


@strawberry.type
@dataclass
class ConvexPoolSnapshot:
    id: str
    poolid: str
    poolName: str
    withdrawalCount: int
    withdrawalVolume: int
    withdrawalValue: float
    depositCount: int
    depositVolume: int
    depositValue: float
    lpTokenBalance: int
    lpTokenVirtualPrice: float
    lpTokenUSDPrice: float
    tvl: float
    curveTvlRatio: float
    baseApr: float
    crvApr: float
    cvxApr: float
    extraRewardsApr: float
    timestamp: int
    block: int


ConvexPoolSnapshotSchema = marshmallow_dataclass.class_schema(ConvexPoolSnapshot)


@dataclass
class ConvexPoolTVLSnapshot:
    tvl: float
    curveTvlRatio: float
    timestamp: int


ConvexPoolTVLSnapshotSchema = marshmallow_dataclass.class_schema(ConvexPoolTVLSnapshot)


@dataclass
class ConvexPoolAPRSnapshot:
    baseApr: float
    crvApr: float
    cvxApr: float
    extraRewardsApr: float
    timestamp: int


ConvexPoolAPRSnapshotSchema = marshmallow_dataclass.class_schema(ConvexPoolAPRSnapshot)


