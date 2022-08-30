from dataclasses import dataclass
import marshmallow_dataclass
import strawberry
from typing import List


@strawberry.type
@dataclass
class ConvexRevenueSnapshot:
    id: str
    crvRevenueToLpProvidersAmount: int
    crvRevenueToCvxCrvStakersAmount: int
    crvRevenueToCvxStakersAmount: int
    crvRevenueToCallersAmount: int
    crvRevenueToPlatformAmount: int
    totalCrvRevenue: int

    crvRevenueToLpProvidersAmountCumulative: int
    crvRevenueToCvxCrvStakersAmountCumulative: int
    crvRevenueToCvxStakersAmountCumulative: int
    crvRevenueToCallersAmountCumulative: int
    crvRevenueToPlatformAmountCumulative: int
    totalCrvRevenueCumulative: int

    crvPrice: float
    timestamp: int


ConvexRevenueSnapshotSchema = marshmallow_dataclass.class_schema(ConvexRevenueSnapshot)


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


