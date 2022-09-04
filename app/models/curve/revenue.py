from dataclasses import dataclass
import marshmallow_dataclass
from typing import List
import strawberry


@dataclass
class CurvePoolRevenue:
    totalDailyFeesUSD: float
    pool: str
    chain: str
    timestamp: int


CurvePoolRevenueSchema = marshmallow_dataclass.class_schema(CurvePoolRevenue)


@dataclass
class CurveChainRevenue:
    totalDailyFeesUSD: float
    chain: str


CurveChainRevenueSchema = marshmallow_dataclass.class_schema(CurveChainRevenue)
