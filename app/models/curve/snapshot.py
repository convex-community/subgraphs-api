from dataclasses import dataclass
import marshmallow_dataclass
from typing import List


@dataclass
class CurvePoolSnapshot:
    id: str
    pool: str
    chain: str
    virtualPrice: float
    lpPriceUSD: float
    tvl: float
    fee: float
    adminFee: float
    totalDailyFeesUSD: float
    reserves: List[int]
    reservesUSD: List[float]
    volume: float
    volumeUSD: float
    baseApr: float
    rebaseApr: float
    timestamp: int


CurvePoolSnapshotSchema = marshmallow_dataclass.class_schema(CurvePoolSnapshot)