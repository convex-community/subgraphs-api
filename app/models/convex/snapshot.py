from dataclasses import dataclass
from marshmallow import Schema, fields
import marshmallow_dataclass


@dataclass
class ConvexPoolSnapshot:
    id: str
    poolid: str
    poolName: str
    swap: str
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


class ConvexPoolSnapshotSchema(Schema):
    id = fields.Str()
    poolid = fields.Str()
    poolName = fields.Str()
    swap = fields.Str()
    withdrawalCount = fields.Int()
    withdrawalVolume = fields.Int()
    withdrawalValue = fields.Float()
    depositCount = fields.Int()
    depositVolume = fields.Int()
    depositValue = fields.Float()
    lpTokenBalance = fields.Int()
    lpTokenVirtualPrice = fields.Float()
    lpTokenUSDPrice = fields.Float()
    tvl = fields.Float()
    curveTvlRatio = fields.Float()
    baseApr = fields.Float(allow_nan=True)
    crvApr = fields.Float()
    cvxApr = fields.Float()
    extraRewardsApr = fields.Float()
    timestamp = fields.Int()
    block = fields.Int()


@dataclass
class ConvexPoolTVLSnapshot:
    tvl: float
    curveTvlRatio: float
    timestamp: int


ConvexPoolTVLSnapshotSchema = marshmallow_dataclass.class_schema(
    ConvexPoolTVLSnapshot
)


@dataclass
class ConvexPoolAPRSnapshot:
    baseApr: float
    crvApr: float
    cvxApr: float
    extraRewardsApr: float
    timestamp: int


ConvexPoolAPRSnapshotSchema = marshmallow_dataclass.class_schema(
    ConvexPoolAPRSnapshot
)
