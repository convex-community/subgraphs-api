from dataclasses import dataclass
from typing import List

import marshmallow_dataclass
from sqlalchemy import (
    Column,
    String,
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    Float,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from main import db


class Market(db.Model):
    __tablename__ = "market"
    id = Column(String, primary_key=True)
    chain = db.Column(db.String, default="mainnet")
    collateral = Column(String)
    collateralName = Column(String)
    collateralPrecision = Column(Integer)
    controller = Column(String)
    amm = Column(String, ForeignKey("amm.id"))
    llama = relationship("Amm")
    monetaryPolicy = Column(String, ForeignKey("monetaryPolicy.id"))
    policy = relationship("MonetaryPolicy")
    index = Column(Integer)
    snapshots = relationship("Snapshot", back_populates="market")
    liquidations = relationship("Liquidation", back_populates="market")


class MonetaryPolicy(db.Model):
    __tablename__ = "monetaryPolicy"
    id = Column(String, primary_key=True)
    market = Column(String)
    pegKeepers = relationship("PegKeeper", back_populates="policy")
    debtFractions = relationship("DebtFraction", back_populates="policy")


class PegKeeper(db.Model):
    __tablename__ = "pegKeeper"
    id = Column(String, primary_key=True)
    policyId = Column(String, ForeignKey("monetaryPolicy.id"))
    policy = relationship("MonetaryPolicy", back_populates="pegKeepers")
    active = Column(Boolean)
    pool = Column(String)
    debt = Column(Numeric)
    totalProvided = Column(Numeric)
    totalWithdrawn = Column(Numeric)
    totalProfit = Column(Numeric)
    historicalDebt = relationship(
        "HistoricalKeeperDebt", back_populates="keeper"
    )


class Liquidation(db.Model):
    __tablename__ = "liquidation"
    id = Column(String, primary_key=True)
    user = Column(String)
    liquidator = Column(String)
    marketId = Column(String, ForeignKey("market.id"))
    market = relationship("Market", back_populates="liquidations")
    collateralReceived = Column(Numeric)
    stablecoinReceived = Column(Numeric)
    collateralReceivedUSD = Column(Numeric)
    oraclePrice = Column(Numeric)
    debt = Column(Numeric)
    blockNumber = Column(Numeric)
    blockTimestamp = Column(Numeric)
    transactionHash = Column(String)


class DebtFraction(db.Model):
    __tablename__ = "debtFraction"
    id = Column(String, primary_key=True)
    policyId = Column(String, ForeignKey("monetaryPolicy.id"))
    policy = relationship("MonetaryPolicy", back_populates="debtFractions")
    target = Column(Numeric)
    blockNumber = Column(Numeric)
    blockTimestamp = Column(Numeric)
    transactionHash = Column(String)


class Amm(db.Model):
    __tablename__ = "amm"
    id = Column(String, primary_key=True)
    market = Column(String)
    coins = Column(ARRAY(String))
    coinNames = Column(ARRAY(String))
    basePrice = Column(Float)
    totalSwapVolume = Column(Float)
    volumeSnapshots = relationship("VolumeSnapshot", back_populates="amm")


class VolumeSnapshot(db.Model):
    __tablename__ = "volumeSnapshot"
    id = Column(String, primary_key=True)
    ammId = Column(String, ForeignKey("amm.id"))
    amm = relationship("Amm", back_populates="volumeSnapshots")
    swapVolumeUsd = Column(Numeric)
    period = Column(Integer)
    count = Column(Integer)
    timestamp = Column(Integer)


class HistoricalKeeperDebt(db.Model):
    __tablename__ = "historical_keeper_debt"
    id = Column(String, primary_key=True)
    keeperId = Column(String, ForeignKey("pegKeeper.id"))
    keeper = relationship("PegKeeper", back_populates="historicalDebt")
    debt = Column(Numeric)
    timestamp = Column(Integer)
    blockNumber = Column(Integer)


class Snapshot(db.Model):
    __tablename__ = "snapshot"
    id = Column(String, primary_key=True)
    marketId = Column(String, ForeignKey("market.id"))
    market = relationship("Market", back_populates="snapshots")
    llammaId = Column(String, ForeignKey("amm.id"))
    llamma = relationship("Amm")
    policyId = Column(String, ForeignKey("monetaryPolicy.id"))
    policy = relationship("MonetaryPolicy")
    A = Column(Integer)
    rate = Column(Numeric)
    futureRate = Column(Numeric)
    liquidationDiscount = Column(Numeric)
    loanDiscount = Column(Numeric)
    minted = Column(Numeric)
    redeemed = Column(Numeric)
    totalKeeperDebt = Column(Numeric)
    totalCollateral = Column(Numeric)
    totalCollateralUsd = Column(Numeric)
    totalSupply = Column(Numeric)
    totalStableCoin = Column(Numeric)
    available = Column(Numeric)
    totalDebt = Column(Numeric)
    nLoans = Column(Integer)
    crvUsdAdminFees = Column(Numeric)
    collateralAdminFees = Column(Numeric)
    adminBorrowingFees = Column(Numeric)
    fee = Column(Numeric)
    adminFee = Column(Numeric)
    ammPrice = Column(Numeric)
    oraclePrice = Column(Numeric)
    basePrice = Column(Numeric)
    activeBand = Column(Integer)
    minBand = Column(Integer)
    maxBand = Column(Integer)
    bandSnapshot = Column(Boolean)
    blockNumber = Column(Integer)
    timestamp = Column(Integer)


class CollectedFees(db.Model):
    __tablename__ = "collectedFees"
    id = Column(String, primary_key=True)
    marketId = Column(String, ForeignKey("market.id"))
    market = relationship("Market")
    borrowingFees = Column(Float)
    ammCollateralFees = Column(Float)
    ammCollateralFeesUsd = Column(Float)
    ammBorrowingFees = Column(Float)
    blockNumber = Column(Integer)
    blockTimestamp = Column(Integer)


class Burn(db.Model):
    __tablename__ = "burns"
    id = Column(String, primary_key=True)
    address = Column(String)
    amount = Column(Float)
    blockNumber = Column(Integer)
    blockTimestamp = Column(Integer)
    transactionHash = Column(String)


class Mint(db.Model):
    __tablename__ = "mints"
    id = Column(String, primary_key=True)
    address = Column(String)
    amount = Column(Float)
    blockNumber = Column(Integer)
    blockTimestamp = Column(Integer)
    transactionHash = Column(String)


class DebtCeiling(db.Model):
    __tablename__ = "debt_ceilings"
    id = Column(String, primary_key=True)
    address = Column(String)
    amount = Column(Float)
    blockNumber = Column(Integer)
    blockTimestamp = Column(Integer)
    transactionHash = Column(String)


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
class Histogram:
    x: List[float]
    y: List[int]


@dataclass
class MarketInfo:
    name: str
    address: str
    llamma: str
    rate: float
    rateAbsDelta: float
    borrowed: float
    borrowedDelta: float
    totalCollateral: float
    totalCollateralDelta: float
    collateral: float
    stableCoin: float
    loans: float
    loansDelta: float


@dataclass
class MarketRate:
    rate: float
    timestamp: int


MarketRateSchema = marshmallow_dataclass.class_schema(MarketRate)


@dataclass
class MarketVolume:
    swapVolumeUsd: float
    timestamp: int


MarketVolumeSchema = marshmallow_dataclass.class_schema(MarketVolume)


@dataclass
class MarketLoans:
    nLoans: int
    timestamp: int


class UserState(db.Model):
    __tablename__ = "user_states"
    id = Column(String, primary_key=True)
    index = Column(Integer)
    user = Column(String)
    marketId = Column(String, ForeignKey("market.id"))
    market = relationship("Market")
    collateral = Column(Numeric)
    collateralUsd = Column(Numeric)
    stableCoin = Column(Numeric)
    debt = Column(Numeric)
    N = Column(Numeric)
    N1 = Column(Numeric)
    N2 = Column(Numeric)
    softLiq = Column(Boolean)
    health = Column(Numeric)
    timestamp = Column(Integer)


class UserStateSnapshot(db.Model):
    __tablename__ = "user_state_snapshots"
    id = Column(String, primary_key=True)
    user = Column(String)
    marketId = Column(String, ForeignKey("market.id"))
    market = relationship("Market")
    activeBand = Column(Float)
    collateral = Column(Float)
    stablecoin = Column(Float)
    oraclePrice = Column(Float)
    collateralUsd = Column(Float)
    collateralUp = Column(Float)
    depositedCollateral = Column(Float)
    debt = Column(Float)
    n = Column(Float)
    n1 = Column(Float)
    n2 = Column(Float)
    health = Column(Float)
    loss = Column(Float)
    lossPct = Column(Float)
    softLiq = Column(Boolean)
    timestamp = Column(Integer)


@dataclass
class UserStateData:
    index: int
    user: str
    collateral: float
    collateralUsd: float
    stableCoin: float
    debt: float
    N: int
    health: float


@dataclass
class TotalSupply:
    name: str
    totalSupply: float
    timestamp: int


TotalSupplySchema = marshmallow_dataclass.class_schema(TotalSupply)


@dataclass
class KeepersDebt:
    keeper: str
    pool: str
    debt: float


@dataclass
class KeepersProfit:
    keeper: str
    pool: str
    profit: float
    market: str


@dataclass
class CrvUsdFees:
    pending: float
    collected: float


@dataclass
class CrvUsdFeesBreakdown:
    market: str
    crvUsdAdminFees: float
    adminBorrowingFees: float
    collateralAdminFeesUsd: float


@dataclass
class CrvUsdYield:
    platform: str
    pool: str
    apy: float


@dataclass
class HistoricalKeeperDebtData:
    keeper: str
    debt: float
    totalKeepersDebt: float
    timestamp: int


@dataclass
class MarketLosers:
    market: str
    marketName: str
    losers: float


@dataclass
class HistoricalMarketLosers:
    timestamp: int
    losers: float


@dataclass
class HistoricalMedianLoss:
    timestamp: int
    lossPct: float


@dataclass
class HistoricalSoftLoss:
    timestamp: int
    collateralPrice: float
    proportion: float


@dataclass
class HealthDistribution:
    decile: str
    collateralUsdValue: float
    stablecoin: float
    debt: float


@dataclass
class HistoricalLiquidations:
    timestamp: int
    selfCount: int
    hardCount: int
    selfValue: float
    hardValue: float
    price: float


@dataclass
class AggregatedLiquidations:
    selfCount: int
    hardCount: int
    selfValue: float
    hardValue: float


@dataclass
class Liquidators:
    address: str
    count: int
    value: float


@dataclass
class HistoricalHealth:
    timestamp: int
    quartiles: List[float]


@dataclass
class MarketHealthState:
    softLiqUsers: int
    softLiqRatio: float
    liqablePositions: int
    liqableDebt: float
    liqableCollatUsd: float
    liqableStable: float
    medianHealth: float
    collatRatio: float


@dataclass
class SupplyEvent:
    timestamp: int
    amount: float


@dataclass
class SupplyAvailable:
    timestamp: int
    borrowable: float
    ceiling: float
