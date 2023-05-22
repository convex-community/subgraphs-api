from dataclasses import dataclass
import marshmallow_dataclass
from typing import List
from flask_restx import fields


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
