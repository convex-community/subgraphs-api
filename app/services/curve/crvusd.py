from typing import List
import pandas as pd
import numpy as np
from sqlalchemy import func, Date, cast

from main import db
from models.curve.crvusd import (
    CrvUsdPoolStatSchema,
    CrvUsdPoolStat,
    Market,
    Snapshot,
    MarketInfo,
    MarketRate,
    MarketRateSchema,
    MarketVolume,
    MarketVolumeSchema,
    VolumeSnapshot,
    MarketLoans,
    Amm,
    UserStateData,
    UserState,
    Histogram,
)
from models.curve.pool import CurvePoolName, CurvePool, CurvePoolNameSchema
from main.const import PoolType, DAY
from models.curve.snapshot import CurvePoolSnapshot
from sqlalchemy import desc, and_
from datetime import timedelta, datetime
import time

from utils import growth_rate


def get_user_states(market_id, timestamp, offset=0, limit=None):
    base_query = db.session.query(UserState).filter(
        UserState.marketId == market_id
    )
    user_states = base_query.filter(UserState.timestamp == timestamp)
    if user_states.count() == 0:
        max_timestamp = (
            base_query.filter(UserState.timestamp < timestamp)
            .with_entities(func.max(UserState.timestamp))
            .scalar()
        )
        if max_timestamp is not None:
            user_states = base_query.filter(
                UserState.timestamp == max_timestamp
            )
    user_states = user_states.order_by(UserState.index).offset(offset)
    if limit is not None:
        user_states = user_states.limit(limit)
    user_states = user_states.all()

    return user_states


def get_latest_user_states(
    market: str, offset: int, limit: int
) -> list[UserStateData]:
    timestamp = int((time.time() // (15 * 60)) * (15 * 60))
    results = get_user_states(market, timestamp, offset, limit)
    return [
        UserStateData(
            index=result.index,
            user=result.user,
            collateral=result.collateral,
            collateralUsd=result.collateralUsd,
            stableCoin=result.stableCoin,
            debt=result.debt,
            N=result.N,
            health=result.health,
        )
        for result in results
    ]


def get_user_health_histogram(market: str):
    timestamp = int((time.time() // (15 * 60)) * (15 * 60))
    results = get_user_states(market, timestamp)
    hist = np.histogram([float(result.health) for result in results], bins=100)
    return Histogram(y=hist[0].tolist(), x=hist[1].tolist())


def get_daily_market_volume(market: str) -> list[MarketVolume]:
    result = (
        db.session.query(
            VolumeSnapshot.swapVolumeUsd, VolumeSnapshot.timestamp
        )
        .join(Amm, Amm.id == VolumeSnapshot.ammId)
        .join(Market, Market.amm == Amm.id)
        .filter(Market.id == market)
        .filter(VolumeSnapshot.period == DAY)
        .order_by(desc(VolumeSnapshot.timestamp))
        .all()
    )
    return [MarketVolumeSchema().load(row._asdict()) for row in result]


def get_hourly_market_rates(market: str) -> list[MarketRate]:
    result = (
        db.session.query(Snapshot.rate, Snapshot.timestamp)
        .join(Market)
        .filter(Snapshot.marketId == market)
        .order_by(desc(Snapshot.timestamp))
        .limit(120)
        .all()
    )
    return [MarketRateSchema().load(row._asdict()) for row in result]


def get_daily_market_rates(market: str) -> list[MarketRate]:
    timestamp_label = cast(func.to_timestamp(Snapshot.timestamp), Date).label(
        "timestamp"
    )
    result = (
        db.session.query(
            timestamp_label, func.avg(Snapshot.rate).label("rate")
        )
        .join(Market)
        .filter(Snapshot.marketId == market)
        .group_by(timestamp_label)
        .order_by(desc(timestamp_label))
        .all()
    )
    return [
        MarketRate(
            rate=rate,
            timestamp=int(
                datetime.combine(timestamp, datetime.min.time()).timestamp()
            ),
        )
        for timestamp, rate in result
    ]


def get_daily_market_loans(market: str) -> list[MarketLoans]:
    timestamp_label = cast(func.to_timestamp(Snapshot.timestamp), Date).label(
        "timestamp"
    )
    result = (
        db.session.query(timestamp_label, func.avg(Snapshot.nLoans))
        .join(Market)
        .filter(Snapshot.marketId == market)
        .group_by(timestamp_label)
        .order_by(desc(timestamp_label))
        .all()
    )
    return [
        MarketLoans(
            nLoans=int(loans),
            timestamp=int(
                datetime.combine(timestamp, datetime.min.time()).timestamp()
            ),
        )
        for timestamp, loans in result
    ]


def get_crv_usd_pool_names() -> list[CurvePoolName]:
    result = (
        db.session.query(CurvePool)
        .with_entities(CurvePool.address, CurvePool.name)
        .filter(CurvePool.poolType == PoolType.CRVUSD.value)
        .all()
    )

    result = [CurvePoolNameSchema().load(row._asdict()) for row in result]

    return result


def get_crv_usd_pool_stats() -> list[CrvUsdPoolStat]:
    subquery = (
        db.session.query(
            CurvePoolSnapshot.pool,
            func.max(CurvePoolSnapshot.timestamp).label("max_timestamp"),
        )
        .group_by(CurvePoolSnapshot.pool)
        .subquery()
    )
    query = (
        db.session.query(
            CurvePool.address,
            CurvePool.name,
            CurvePoolSnapshot.tvl,
            CurvePoolSnapshot.normalizedReserves,
            CurvePoolSnapshot.reservesUSD,
            CurvePoolSnapshot.volumeUSD,
        )
        .join(CurvePoolSnapshot, CurvePool.address == CurvePoolSnapshot.pool)
        .join(
            subquery,
            and_(
                CurvePoolSnapshot.pool == subquery.c.pool,
                CurvePoolSnapshot.timestamp == subquery.c.max_timestamp,
            ),
        )
        .filter(CurvePool.poolType == PoolType.CRVUSD.value)
    )
    results = []
    for row in query.all():
        result = CrvUsdPoolStatSchema().load(row._asdict())
        result.name = result.name.split("Pool: ")[-1]
        results.append(result)

    return results


def get_crvusd_markets() -> List[MarketInfo]:

    now = time.time()
    one_day_ago = now - timedelta(days=1).total_seconds()

    markets = db.session.query(Market).all()
    res = []
    for market in markets:
        last_snapshot = (
            db.session.query(Snapshot)
            .filter_by(marketId=market.id)
            .order_by(desc(Snapshot.timestamp))
            .first()
        )
        snapshot_one_day_ago = (
            db.session.query(Snapshot)
            .filter(
                and_(
                    Snapshot.marketId == market.id,
                    Snapshot.timestamp <= one_day_ago,
                )
            )
            .order_by(desc(Snapshot.timestamp))
            .first()
        )

        last_snapshot_rate = last_snapshot.rate if last_snapshot else 0
        last_snapshot_nLoans = last_snapshot.nLoans if last_snapshot else 0
        last_snapshot_totalCollateralUsd = (
            last_snapshot.totalCollateralUsd if last_snapshot else 0
        )
        last_snapshot_totalStableCoin = (
            last_snapshot.totalStableCoin if last_snapshot else 0
        )
        last_snapshot_totalDebt = (
            last_snapshot.totalDebt if last_snapshot else 0
        )

        snapshot_one_day_ago_rate = (
            snapshot_one_day_ago.rate
            if snapshot_one_day_ago
            else last_snapshot.rate
        )
        snapshot_one_day_ago_nLoans = (
            snapshot_one_day_ago.nLoans
            if snapshot_one_day_ago
            else last_snapshot.nLoans
        )
        snapshot_one_day_ago_totalCollateralUsd = (
            snapshot_one_day_ago.totalCollateralUsd
            if snapshot_one_day_ago
            else last_snapshot.totalCollateralUsd
        )
        snapshot_one_day_ago_totalStableCoin = (
            snapshot_one_day_ago.totalStableCoin
            if snapshot_one_day_ago
            else last_snapshot.totalStableCoin
        )
        snapshot_one_day_ago_totalDebt = (
            snapshot_one_day_ago.totalDebt
            if snapshot_one_day_ago
            else last_snapshot.totalDebt
        )

        last_total_collateral = (
            last_snapshot_totalCollateralUsd + last_snapshot_totalStableCoin
        )
        snapshot_one_day_ago_collateral = (
            snapshot_one_day_ago_totalCollateralUsd
            + snapshot_one_day_ago_totalStableCoin
        )
        res.append(
            MarketInfo(
                name=market.collateralName,
                address=market.id,
                rate=last_snapshot_rate,
                rateDelta=growth_rate(
                    last_snapshot_rate, snapshot_one_day_ago_rate
                ),
                borrowed=last_snapshot_totalDebt,
                borrowedDelta=growth_rate(
                    last_snapshot_totalDebt, snapshot_one_day_ago_totalDebt
                ),
                totalCollateral=last_total_collateral,
                totalCollateralDelta=growth_rate(
                    last_total_collateral, snapshot_one_day_ago_collateral
                ),
                collateral=last_snapshot_totalCollateralUsd,
                stableCoin=last_snapshot_totalStableCoin,
                loans=last_snapshot_nLoans,
                loansDelta=growth_rate(
                    last_snapshot_nLoans, snapshot_one_day_ago_nLoans
                ),
            )
        )
    return res
