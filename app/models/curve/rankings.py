from dataclasses import dataclass


@dataclass
class TopTvlChange:
    pool: str
    chain: str
    name: str
    tvl_growth: float


@dataclass
class PoolTypeVolume:
    type: str
    volumeUSD: float


@dataclass
class PoolTypeTvl:
    type: str
    tvl: float


@dataclass
class ChainVolume:
    chain: str
    volumeUSD: float


@dataclass
class ChainTvl:
    chain: str
    tvl: float


@dataclass
class TopLiquidityUse:
    pool: str
    chain: str
    name: str
    liq_use: float


@dataclass
class LargeTrades:
    pool: str
    chain: str
    name: str
    tx: str
    value: float
