from typing import List, Optional
import pandas as pd
import numpy as np
from sqlalchemy import func, Date, cast, Integer, text, literal, label

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
    TotalSupply,
    TotalSupplySchema,
    PegKeeper,
    KeepersDebt,
    CollectedFees,
    CrvUsdFeesBreakdown,
    CrvUsdFees,
    MonetaryPolicy,
    KeepersProfit,
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
    def generate_deciles(df, decimals=3):
        bins = np.percentile(df.health, np.arange(0, 110, 10))
        labels = [
            f"[{round(el * 100, decimals) if i != 0 else 0}, {round(bins[i + 1] * 100, decimals) if i < len(bins) - 2 else 1})"
            for i, el in enumerate(bins[:-1])
        ]
        return pd.cut(
            df["health"].apply(lambda x: round(x, decimals)),
            bins=bins,
            labels=labels,
        )

    timestamp = int((time.time() // (15 * 60)) * (15 * 60))
    states = get_user_states(market, timestamp)
    results = pd.DataFrame([s.__dict__ for s in states])
    results[
        ["health", "debt", "collateral", "collateralUsd", "stableCoin"]
    ] = results[
        ["health", "debt", "collateral", "collateralUsd", "stableCoin"]
    ].astype(
        float
    )

    try:
        results["interval"] = generate_deciles(results)
    except ValueError:
        results["interval"] = generate_deciles(results, 10)
    return (
        results[
            ["debt", "collateral", "collateralUsd", "stableCoin", "interval"]
        ]
        .groupby("interval")
        .sum()
        .to_dict("index")
    )


def get_volume_snapshot(
    market_id: str, period: int, start_date: int, end_date: int
) -> list[MarketVolume]:
    result = (
        db.session.query(
            VolumeSnapshot.swapVolumeUsd, VolumeSnapshot.timestamp
        )
        .join(Amm, Amm.id == VolumeSnapshot.ammId)
        .join(Market, Market.amm == Amm.id)
        .filter(Market.id == market_id)
        .filter(VolumeSnapshot.period == period)
        .filter(VolumeSnapshot.timestamp >= start_date)
        .filter(VolumeSnapshot.timestamp <= end_date)
        .order_by(desc(VolumeSnapshot.timestamp))
        .all()
    )
    return [MarketVolumeSchema().load(row._asdict()) for row in result]


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


def get_crvusd_markets(
    market_address: Optional[str] = None,
) -> List[MarketInfo]:

    now = time.time()
    one_day_ago = now - timedelta(days=1).total_seconds()

    query = db.session.query(Market)
    if market_address:
        query = query.filter(Market.controller == market_address)

    markets = query.all()
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
                rateAbsDelta=last_snapshot_rate - snapshot_one_day_ago_rate,
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


def get_historical_supply():
    snapshot_subquery = (
        db.session.query(
            Snapshot.marketId,
            func.date_trunc(
                "day", func.to_timestamp(Snapshot.timestamp)
            ).label("day"),
            func.max(Snapshot.timestamp).label("last_timestamp"),
        )
        .group_by(Snapshot.marketId, "day")
        .subquery()
    )

    keepers_snapshot_subquery = (
        db.session.query(
            func.date_trunc(
                "day", func.to_timestamp(Snapshot.timestamp)
            ).label("day"),
            func.max(Snapshot.timestamp).label("last_timestamp"),
        )
        .group_by("day")
        .subquery()
    )

    supply_subquery = db.session.query(
        Snapshot.marketId,
        Snapshot.timestamp,
        (Snapshot.minted - Snapshot.redeemed).label("totalSupply"),
        Snapshot.totalKeeperDebt.label("keepersDebt"),
    ).subquery()

    market_results = (
        db.session.query(
            Market.collateralName.label("name"),
            func.extract("epoch", snapshot_subquery.c.day)
            .cast(Integer)
            .label("timestamp"),
            func.sum(supply_subquery.c.totalSupply).label("totalSupply"),
        )
        .join(
            supply_subquery,
            and_(
                supply_subquery.c.marketId == snapshot_subquery.c.marketId,
                supply_subquery.c.timestamp
                == snapshot_subquery.c.last_timestamp,
            ),
        )
        .join(Market, Market.id == supply_subquery.c.marketId)
        .group_by(
            "name",
            "timestamp",
            snapshot_subquery.c.day,  # Include 'day' in the GROUP BY clause
        )
        .order_by("timestamp")
        .all()
    )

    keepers_debt_results = (
        db.session.query(
            literal("Keepers debt").label("name"),
            func.extract("epoch", keepers_snapshot_subquery.c.day)
            .cast(Integer)
            .label("timestamp"),
            Snapshot.totalKeeperDebt.label("totalSupply"),
        )
        .join(
            Snapshot,
            Snapshot.timestamp == keepers_snapshot_subquery.c.last_timestamp,
        )
        .group_by(
            "name",
            "timestamp",
            keepers_snapshot_subquery.c.day,
            Snapshot.totalKeeperDebt,
        )
        .order_by("timestamp")
        .all()
    )

    results = market_results + keepers_debt_results

    df = pd.DataFrame(results, columns=["name", "timestamp", "totalSupply"])
    df2 = (
        df.drop_duplicates()
        .pivot_table(values=["totalSupply"], columns="name", index="timestamp")
        .fillna(0)
        .sort_values("timestamp", ascending=False)
    )
    df2.columns = df2.columns.droplevel()
    df2 = df2.reset_index().melt(
        id_vars="timestamp", var_name="name", value_name="totalSupply"
    )
    df2.sort_values(
        ["timestamp", "name"], ascending=[False, True], inplace=True
    )
    return TotalSupplySchema().load(df2.to_dict("records"), many=True)


def get_keepers_debt():
    keepers = db.session.query(PegKeeper).all()
    return [
        KeepersDebt(
            keeper=keeper.id, pool=keeper.pool, debt=float(keeper.debt) * 1e-18
        )
        for keeper in keepers
    ]


def get_keepers_profit():
    keepers = (
        db.session.query(PegKeeper, MonetaryPolicy, Market)
        .join(MonetaryPolicy, PegKeeper.policyId == MonetaryPolicy.id)
        .join(Market, MonetaryPolicy.market == Market.id)
        .all()
    )
    return [
        KeepersProfit(
            keeper=keeper.PegKeeper.id,
            pool=keeper.PegKeeper.pool,
            profit=float(keeper.PegKeeper.totalProfit) * 1e-18,
            market=keeper.Market.id,
        )
        for keeper in keepers
    ]


def get_pending_fees_from_snapshot(
    market_id=None,
) -> List[CrvUsdFeesBreakdown]:
    subquery = db.session.query(
        Snapshot.marketId,
        func.max(Snapshot.timestamp).label("max_timestamp"),
    ).group_by(Snapshot.marketId)

    # If a market_id is specified, add a where clause to the subquery
    if market_id is not None:
        subquery = subquery.filter(Snapshot.marketId == market_id)

    subquery = subquery.subquery()

    query = db.session.query(
        Snapshot.marketId,
        Snapshot.crvUsdAdminFees,
        Snapshot.adminBorrowingFees,
        label(
            "collateralAdminFeesUsd",
            Snapshot.collateralAdminFees * Snapshot.oraclePrice,
        ),
    ).join(
        subquery,
        and_(
            Snapshot.marketId == subquery.c.marketId,
            Snapshot.timestamp == subquery.c.max_timestamp,
        ),
    )

    # If a market_id is specified, add a where clause to the query
    if market_id is not None:
        query = query.filter(Snapshot.marketId == market_id)

    results = query.all()

    return [
        CrvUsdFeesBreakdown(
            market=result.marketId,
            crvUsdAdminFees=result.crvUsdAdminFees,
            adminBorrowingFees=result.adminBorrowingFees,
            collateralAdminFeesUsd=result.collateralAdminFeesUsd,
        )
        for result in results
    ]


def get_total_collected_fees(market_id=None):
    query = db.session.query(
        CollectedFees.marketId,
        func.coalesce(func.sum(CollectedFees.borrowingFees), 0).label(
            "total_borrowingFees"
        ),
        func.coalesce(func.sum(CollectedFees.ammCollateralFees), 0).label(
            "total_ammCollateralFees"
        ),
        func.coalesce(func.sum(CollectedFees.ammCollateralFeesUsd), 0).label(
            "total_ammCollateralFeesUsd"
        ),
        func.coalesce(func.sum(CollectedFees.ammBorrowingFees), 0).label(
            "total_ammBorrowingFees"
        ),
    )

    # If a market_id is specified, add a where clause to the query
    if market_id is not None:
        query = query.filter(CollectedFees.marketId == market_id)

    results = query.group_by(CollectedFees.marketId).all()

    return [
        CrvUsdFeesBreakdown(
            market=result.marketId,
            crvUsdAdminFees=result.total_borrowingFees,
            adminBorrowingFees=result.total_ammCollateralFees,
            collateralAdminFeesUsd=result.total_ammCollateralFeesUsd,
        )
        for result in results
    ]


def get_aggregated_fees(market_id=None):
    pending = sum(
        [
            (
                c.crvUsdAdminFees
                + c.adminBorrowingFees
                + c.collateralAdminFeesUsd
            )
            for c in get_pending_fees_from_snapshot(market_id)
        ]
    )
    collected = sum(
        [
            (
                c.crvUsdAdminFees
                + c.adminBorrowingFees
                + c.collateralAdminFeesUsd
            )
            for c in get_total_collected_fees(market_id)
        ]
    )
    return CrvUsdFees(pending=pending, collected=collected)


def get_fees_breakdown(market_id=None):
    return {
        "pending": get_pending_fees_from_snapshot(market_id),
        "collected": get_total_collected_fees(market_id),
    }
