from dataclasses import dataclass
from sqlalchemy import Column, Integer, Numeric, String, Float
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import marshmallow_dataclass
from main import db


class ConvexPoolSnapshot(db.Model):
    __tablename__ = "convex_pool_snapshot"

    id = Column(String, primary_key=True)
    poolid = Column(String)
    poolName = Column(String)
    swap = Column(String)
    withdrawalCount = Column(Numeric)
    withdrawalVolume = Column(Numeric)
    withdrawalValue = Column(Float)
    depositCount = Column(Integer)
    depositVolume = Column(Numeric)
    depositValue = Column(Float)
    lpTokenBalance = Column(Numeric)
    lpTokenVirtualPrice = Column(Float)
    lpTokenUSDPrice = Column(Float)
    tvl = Column(Float)
    curveTvlRatio = Column(Float)
    baseApr = Column(Float)
    crvApr = Column(Float)
    cvxApr = Column(Float)
    extraRewardsApr = Column(Float)
    timestamp = Column(Integer)
    block = Column(Integer)


class ConvexPoolSnapshotSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ConvexPoolSnapshot
        load_instance = True  # Optional: deserialize to model instances


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
