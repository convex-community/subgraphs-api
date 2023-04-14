from dataclasses import dataclass
import marshmallow_dataclass
from typing import List


@dataclass
class CurvePoolIlCalcData:
    lpPriceUSD: float
    normalizedReserves: List[int]
    reservesUSD: List[float]
    tvl: int
    timestamp: int


CurvePoolIlCalcDataSchema = marshmallow_dataclass.class_schema(
    CurvePoolIlCalcData
)


@dataclass
class LpHodlXyk:
    curve: float
    hodl: float
    xyk: float
    timestamp: int


@dataclass
class ConvexAprData:
    crvApr: float
    cvxApr: float
    extraRewardsApr: float
    timestamp: int


ConvexAprDataSchema = marshmallow_dataclass.class_schema(ConvexAprData)


@dataclass
class CurveReturnSeries:
    curve: float
    hodl: float
    xyk: float
    curve_rewards: float
    timestamp: int


CurveReturnSeriesSchema = marshmallow_dataclass.class_schema(CurveReturnSeries)
