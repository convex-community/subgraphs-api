from dataclasses import dataclass
import marshmallow_dataclass
from typing import List


@dataclass
class CurvePoolIlCalcData:
    lpPriceUSD: float
    normalizedReserves: List[int]
    reservesUSD: List[float]
    tvl: int
    timestamp: int


CurvePoolIlCalcDataSchema = marshmallow_dataclass.class_schema(
    CurvePoolIlCalcData
)
