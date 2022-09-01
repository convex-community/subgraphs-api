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
class ConvexCumulativeRevenue:
    crvRevenueToLpProvidersAmountCumulative: int
    crvRevenueToCvxCrvStakersAmountCumulative: int
    crvRevenueToCvxStakersAmountCumulative: int
    crvRevenueToCallersAmountCumulative: int
    crvRevenueToPlatformAmountCumulative: int
    totalCrvRevenueCumulative: int
    crvPrice: float


ConvexCumulativeRevenueSchema = marshmallow_dataclass.class_schema(ConvexCumulativeRevenue)


@dataclass
class ConvexHistoricalRevenueSnapshot:
    crvRevenueToLpProvidersAmount: int
    crvRevenueToCvxCrvStakersAmount: int
    crvRevenueToCvxStakersAmount: int
    crvRevenueToCallersAmount: int
    crvRevenueToPlatformAmount: int
    crvPrice: float
    timestamp: int


ConvexHistoricalRevenueSnapshotSchema = marshmallow_dataclass.class_schema(ConvexHistoricalRevenueSnapshot)


