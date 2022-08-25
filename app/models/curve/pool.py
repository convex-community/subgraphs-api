from dataclasses import dataclass
import marshmallow_dataclass
import strawberry
from typing import List


@strawberry.type
@dataclass
class CurvePool:
    id: str
    address: str
    name: str
    symbol: str
    chain: str
    lpToken: str
    coins: List[str]
    coinNames: List[str]
    isV2: bool
    cumulativeVolumeUSD: float
    cumulativeFeesUSD: float
    virtualPrice: float
    baseApr: float


CurvePoolSchema = marshmallow_dataclass.class_schema(CurvePool)


@dataclass
class CurvePoolName:
    address: str
    name: str


CurvePoolNameSchema = marshmallow_dataclass.class_schema(CurvePoolName)
