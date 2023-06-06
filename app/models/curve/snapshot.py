from dataclasses import dataclass
import marshmallow_dataclass
from typing import List
from sqlalchemy import Column, Integer, Float, String, Numeric
from sqlalchemy.dialects.postgresql import ARRAY
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from main import db


class CurvePoolSnapshot(db.Model):
    __tablename__ = "curve_pool_snapshot"

    id = Column(String, primary_key=True)
    pool = Column(String)
    chain = Column(String)
    virtualPrice = Column(Float)
    A = Column(Numeric)
    lpPriceUSD = Column(Float)
    tvl = Column(Float)
    fee = Column(Float)
    adminFee = Column(Float)
    totalDailyFeesUSD = Column(Float)
    reserves = Column(ARRAY(Numeric))
    normalizedReserves = Column(ARRAY(Numeric))
    reservesUSD = Column(ARRAY(Float))
    volume = Column(Float)
    volumeUSD = Column(Float)
    baseApr = Column(Float)
    rebaseApr = Column(Float)
    timestamp = Column(Integer)


class CurvePoolSnapshotSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = CurvePoolSnapshot
        load_instance = True


@dataclass
class CurvePoolVolumeSnapshot:
    volume: float
    volumeUSD: float
    timestamp: int


CurvePoolVolumeSnapshotSchema = marshmallow_dataclass.class_schema(
    CurvePoolVolumeSnapshot
)


@dataclass
class CurvePoolFeeSnapshot:
    totalDailyFeesUSD: float
    adminFee: float
    fee: float
    timestamp: int


CurvePoolFeeSnapshotSchema = marshmallow_dataclass.class_schema(
    CurvePoolFeeSnapshot
)


@dataclass
class CurvePoolTVLSnapshot:
    tvl: float
    timestamp: int


CurvePoolTVLSnapshotSchema = marshmallow_dataclass.class_schema(
    CurvePoolTVLSnapshot
)


@dataclass
class CurvePoolReserveSnapshot:
    reserves: List[int]
    reservesUSD: List[float]
    timestamp: int


CurvePoolReserveSchema = marshmallow_dataclass.class_schema(
    CurvePoolReserveSnapshot
)
