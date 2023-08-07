from dataclasses import dataclass
from marshmallow_dataclass import class_schema

from sqlalchemy import Column, Integer, Float, String
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from main import db


class ConvexRevenueSnapshot(db.Model):
    __tablename__ = "convex_revenue_snapshot"

    id = Column(String, primary_key=True)
    crvRevenueToLpProvidersAmount = Column(Float)
    cvxRevenueToLpProvidersAmount = Column(Float)
    crvRevenueToCvxCrvStakersAmount = Column(Float)
    cvxRevenueToCvxCrvStakersAmount = Column(Float)
    threeCrvRevenueToCvxCrvStakersAmount = Column(Float)
    crvRevenueToCvxStakersAmount = Column(Float)
    crvRevenueToCallersAmount = Column(Float)
    crvRevenueToPlatformAmount = Column(Float)
    totalCrvRevenue = Column(Float)
    fxsRevenueToCvxStakersAmount = Column(Float)
    fxsRevenueToCvxFxsStakersAmount = Column(Float)
    fxsRevenueToLpProvidersAmount = Column(Float)
    fxsRevenueToCallersAmount = Column(Float)
    fxsRevenueToPlatformAmount = Column(Float)
    totalFxsRevenue = Column(Float)
    otherRevenue = Column(Float)
    bribeRevenue = Column(Float)
    cvxPrice = Column(Float)
    fxsPrice = Column(Float)
    crvPrice = Column(Float)
    timestamp = Column(Integer)


class ConvexRevenueSnapshotSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ConvexRevenueSnapshot
        load_instance = True


@dataclass
class ConvexRevenueSnapshotData:
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
    timestamp: int


ConvexRevenueSnapshotDataSchema = class_schema(ConvexRevenueSnapshotData)()


class ConvexCumulativeRevenue(db.Model):
    __tablename__ = "convex_cumulative_revenue"

    id = Column(String, primary_key=True)
    totalCrvRevenueToLpProviders = Column(Float)
    totalCvxRevenueToLpProviders = Column(Float)
    totalFxsRevenueToLpProviders = Column(Float)
    totalCrvRevenueToCvxCrvStakers = Column(Float)
    totalCvxRevenueToCvxCrvStakers = Column(Float)
    totalThreeCrvRevenueToCvxCrvStakers = Column(Float)
    totalFxsRevenueToCvxFxsStakers = Column(Float)
    totalCrvRevenueToCvxStakers = Column(Float)
    totalFxsRevenueToCvxStakers = Column(Float)
    totalCrvRevenueToCallers = Column(Float)
    totalFxsRevenueToCallers = Column(Float)
    totalCrvRevenueToPlatform = Column(Float)
    totalFxsRevenueToPlatform = Column(Float)
    totalCrvRevenue = Column(Float)
    totalFxsRevenue = Column(Float)
    totalOtherRevenue = Column(Float)
    totalBribeRevenue = Column(Float)


class ConvexCumulativeRevenueSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ConvexCumulativeRevenue
        load_instance = True
