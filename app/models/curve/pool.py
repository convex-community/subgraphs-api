from dataclasses import dataclass
from marshmallow import fields
import marshmallow_dataclass
from dataclasses import field
from typing import List


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
