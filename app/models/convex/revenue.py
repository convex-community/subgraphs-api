from dataclasses import dataclass
import marshmallow_dataclass
import strawberry


@strawberry.type
@dataclass
class ConvexRevenueSnapshot:
    id: str
    crvRevenueToLpProvidersAmount: float
    cvxRevenueToLpProvidersAmount: float
    crvRevenueToCvxCrvStakersAmount: float
    cvxRevenueToCvxCrvStakersAmount: float
    threeCrvRevenueToCvxCrvStakersAmount: float
    crvRevenueToCvxStakersAmount: float
    crvRevenueToCallersAmount: float
    crvRevenueToPlatformAmount: float
    totalCrvRevenue: float
    fxsRevenueToCvxStakersAmount: float
    fxsRevenueToCvxFxsStakersAmount: float
    fxsRevenueToLpProvidersAmount: float
    fxsRevenueToCallersAmount: float
    fxsRevenueToPlatformAmount: float
    totalFxsRevenue: float
    otherRevenue: float
    bribeRevenue: float
    cvxPrice: float
    fxsPrice: float
    crvPrice: float
    timestamp: int


ConvexRevenueSnapshotSchema = marshmallow_dataclass.class_schema(
    ConvexRevenueSnapshot
)


@dataclass
class ConvexCumulativeRevenue:
    totalCrvRevenueToLpProviders: float
    totalCvxRevenueToLpProviders: float
    totalFxsRevenueToLpProviders: float
    totalCrvRevenueToCvxCrvStakers: float
    totalCvxRevenueToCvxCrvStakers: float
    totalThreeCrvRevenueToCvxCrvStakers: float
    totalFxsRevenueToCvxFxsStakers: float
    totalCrvRevenueToCvxStakers: float
    totalFxsRevenueToCvxStakers: float
    totalCrvRevenueToCallers: float
    totalFxsRevenueToCallers: float
    totalCrvRevenueToPlatform: float
    totalFxsRevenueToPlatform: float
    totalCrvRevenue: float
    totalFxsRevenue: float
    totalOtherRevenue: float
    totalBribeRevenue: float


ConvexCumulativeRevenueSchema = marshmallow_dataclass.class_schema(
    ConvexCumulativeRevenue
)
