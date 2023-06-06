from dataclasses import dataclass
from typing import List

import marshmallow_dataclass


@dataclass
class CrvUsdPoolStat:
    address: str
    name: str
    tvl: float
    normalizedReserves: List[float]
    reservesUSD: List[float]
    volumeUSD: float


CrvUsdPoolStatSchema = marshmallow_dataclass.class_schema(CrvUsdPoolStat)


@dataclass
class CrvUsdPriceHistogram:
    x: List[float]
    y: List[int]
