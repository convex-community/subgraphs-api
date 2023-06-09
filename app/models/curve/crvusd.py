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
    debt = Column(Numeric)
    totalProvided = Column(Numeric)
    totalWithdrawn = Column(Numeric)
    totalProfit = Column(Numeric)


class Liquidation(db.Model):
    __tablename__ = "liquidation"
    id = Column(String, primary_key=True)
    user = Column(String)
    liquidator = Column(String)
    marketId = Column(String, ForeignKey("market.id"))
    market = relationship("Market", back_populates="liquidations")
    collateralReceived = Column(Numeric)
    stablecoinReceived = Column(Numeric)
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
    totalDepositVolume = Column(Float)
    totalVolume = Column(Float)
    volumeSnapshots = relationship("VolumeSnapshot", back_populates="amm")


class VolumeSnapshot(db.Model):
    __tablename__ = "volumeSnapshot"
    id = Column(String, primary_key=True)
    ammId = Column(String, ForeignKey("amm.id"))
    amm = relationship("Amm", back_populates="volumeSnapshots")
    swapVolumeUsd = Column(Numeric)
    depositVolumeUsd = Column(Numeric)
    totalVolumeUsd = Column(Numeric)
    period = Column(Integer)
    count = Column(Integer)
    timestamp = Column(Integer)


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
    totalDebt = Column(Numeric)
    nLoans = Column(Integer)
    crvUsdAdminFees = Column(Numeric)
    collateralAdminFees = Column(Numeric)
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


@dataclass
class MarketInfo:
    name: str
    address: str
    rate: float
    rateDelta: float
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
