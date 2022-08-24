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


@dataclass
class CurvePoolVolumeSnapshot:
    volume: float
    volumeUSD: float
    timestamp: int


CurvePoolVolumeSnapshotSchema = marshmallow_dataclass.class_schema(CurvePoolVolumeSnapshot)


@dataclass
class CurvePoolFeeSnapshot:
    totalDailyFeesUSD: float
    adminFee: float
    fee: float
    timestamp: int


CurvePoolFeeSnapshotSchema = marshmallow_dataclass.class_schema(CurvePoolFeeSnapshot)


@dataclass
class CurvePoolTVLSnapshot:
    tvl: float
    timestamp: int


CurvePoolTVLSnapshotSchema = marshmallow_dataclass.class_schema(CurvePoolTVLSnapshot)


@dataclass
class CurvePoolReserveSnapshot:
    reserves: List[int]
    reservesUSD: List[float]
    timestamp: int


CurvePoolReserveSchema = marshmallow_dataclass.class_schema(CurvePoolReserveSnapshot)
