from dataclasses import dataclass
import marshmallow_dataclass
from typing import List


@dataclass
class CurvePool:
    id: str
    address: str
    name: str
    symbol: str
    lpToken: str
    coins: List[str]
    coinNames: List[str]
    isV2: bool
    cumulativeVolumeUSD: float
    cumulativeFeesUSD: float
    virtualPrice: float
    baseApr: float


CurvePoolSchema = marshmallow_dataclass.class_schema(CurvePool
)