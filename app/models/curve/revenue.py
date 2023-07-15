from dataclasses import dataclass
from typing import List

import marshmallow_dataclass
from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from main import db


@dataclass
class CurvePoolRevenue:
    totalDailyFeesUSD: float
    pool: str
    chain: str
    timestamp: int


CurvePoolRevenueSchema = marshmallow_dataclass.class_schema(CurvePoolRevenue)


@dataclass
class CurveChainRevenue:
    chain: str
    totalDailyFeesUSD: float


CurveChainRevenueSchema = marshmallow_dataclass.class_schema(CurveChainRevenue)


@dataclass
class CurveChainTopPoolRevenue:
    name: str
    totalDailyFeesUSD: float


CurveChainTopPoolRevenueSchema = marshmallow_dataclass.class_schema(
    CurveChainTopPoolRevenue
)


@dataclass
class CurveHistoricalPoolCumulativeRevenue:
    pool: str
    timestamp: int
    revenue: float


CurveHistoricalPoolCumulativeRevenueSchema = (
    marshmallow_dataclass.class_schema(CurveHistoricalPoolCumulativeRevenue)
)


class CouchInfo(db.Model):
    __tablename__ = "couch_info"

    id = Column(String, primary_key=True)
    poolId = Column(String, ForeignKey("curve_pool.id"))
    pool = relationship("CurvePool")
    balance = Column(ARRAY(Float))
    value = Column(ARRAY(Float))
    totalUSD = Column(Float)


@dataclass
class CouchCushion:
    pool: str
    address: str
    chain: str
    coins: List[str]
    coinNames: List[str]
    balance: List[float]
    value: List[float]
    totalUSD: float
