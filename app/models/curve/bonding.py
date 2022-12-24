from dataclasses import dataclass
from typing import List
import marshmallow_dataclass


@dataclass
class CurvePoolBondingCurve:
    coin0: str
    coin1: str
    x: List[int]
    y: List[int]


CurvePoolBondingCurveSchema = marshmallow_dataclass.class_schema(
    CurvePoolBondingCurve
)
