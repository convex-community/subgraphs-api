from dataclasses import dataclass
import marshmallow_dataclass
from typing import List
import strawberry
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
class CurveHistoricalPoolCumulativeRevenue:
    name: str
    timestamp: int
    cumulativeDailyFeesUSD: float


CurveHistoricalPoolCumulativeRevenueSchema = (
    marshmallow_dataclass.class_schema(CurveHistoricalPoolCumulativeRevenue)
)
