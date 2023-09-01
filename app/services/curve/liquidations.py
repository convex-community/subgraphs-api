from sqlalchemy import func

from main import db
from models.curve.crvusd import (
    UserStateSnapshot,
    Market,
    MarketLosers,
    HistoricalMarketLosers,
    HistoricalMedianLoss,
    HistoricalSoftLoss,
    HealthDistribution,
)
import pandas as pd


def get_loser_proportions():
    subquery = (
        db.session.query(
            UserStateSnapshot.marketId,
            func.max(UserStateSnapshot.timestamp).label("max_timestamp"),
        )
        .group_by(UserStateSnapshot.marketId)
        .subquery()
    )

    results = (
        db.session.query(UserStateSnapshot, Market.collateralName)
        .join(Market, Market.id == UserStateSnapshot.marketId)
        .join(
            subquery,
            (UserStateSnapshot.marketId == subquery.c.marketId)
            & (UserStateSnapshot.timestamp == subquery.c.max_timestamp),
        )
        .all()
    )
    df = pd.DataFrame(
        [
            (
                r.UserStateSnapshot.marketId,
                r.UserStateSnapshot.loss > 0,
                r.collateralName,
            )
            for r in results
        ],
        columns=["market", "has_loss", "collateralName"],
    )
    if df.empty:
        return []
    df_pivot = (
        df.groupby(["market", "collateralName", "has_loss"])
        .size()
        .unstack(fill_value=0)
    )

    df_pivot["proportion"] = (
        df_pivot[True] / (df_pivot[True] + df_pivot[False]) * 100
    )

    return [
        MarketLosers(
            market=index[0], marketName=index[1], losers=row["proportion"]
        )
        for index, row in df_pivot.iterrows()
    ]


def get_historical_loser_proportions(market_id):
    query = (
        db.session.query(
            UserStateSnapshot.timestamp, UserStateSnapshot.lossPct
        )
        .join(Market, Market.id == UserStateSnapshot.marketId)
        .filter(func.lower(Market.id) == market_id.lower())
        .order_by(UserStateSnapshot.timestamp)
    ).all()
    df = pd.DataFrame(query, columns=["timestamp", "lossPct"])
    df["has_loss"] = df["lossPct"] > 0
    loss_prop = df.groupby("timestamp")["has_loss"].mean() * 100
    return [HistoricalMarketLosers(ts, prop) for ts, prop in loss_prop.items()]


def get_historical_median_loss(market_id):
    query = (
        db.session.query(
            UserStateSnapshot.timestamp, UserStateSnapshot.lossPct
        )
        .join(Market, Market.id == UserStateSnapshot.marketId)
        .filter(func.lower(Market.id) == market_id.lower())
        .filter(UserStateSnapshot.lossPct > 0)
        .order_by(UserStateSnapshot.timestamp)
    ).all()
    df = pd.DataFrame(query, columns=["timestamp", "lossPct"])
    loss_prop = df.groupby("timestamp")["lossPct"].median()
    return [HistoricalMedianLoss(ts, prop) for ts, prop in loss_prop.items()]


def get_historical_soft_loss(market_id):
    query = (
        db.session.query(
            UserStateSnapshot.timestamp,
            UserStateSnapshot.user,
            UserStateSnapshot.softLiq,
            UserStateSnapshot.oraclePrice,
        )
        .join(Market, Market.id == UserStateSnapshot.marketId)
        .filter(func.lower(Market.id) == market_id.lower())
        .order_by(UserStateSnapshot.timestamp)
    ).all()
    df = pd.DataFrame(
        query, columns=["timestamp", "user", "softLiq", "oraclePrice"]
    )

    grouped = df.groupby("timestamp").agg(
        total_users=("user", "size"),
        softLiq_true_count=("softLiq", lambda x: x.sum()),
    )
    grouped["percentage_softLiq"] = (
        grouped["softLiq_true_count"] / grouped["total_users"]
    ) * 100
    df2 = (
        df[["timestamp", "oraclePrice"]]
        .drop_duplicates()
        .set_index("timestamp")
    )
    final_df = grouped.join(df2, on="timestamp")
    return [
        HistoricalSoftLoss(ts, row["oraclePrice"], row["percentage_softLiq"])
        for ts, row in final_df.iterrows()
    ]


def get_health_distribution(market_id):
    subquery = (
        db.session.query(func.max(UserStateSnapshot.timestamp))
        .join(Market, Market.id == UserStateSnapshot.marketId)
        .filter(func.lower(Market.id) == market_id.lower())
    ).scalar()

    query = (
        db.session.query(
            UserStateSnapshot.timestamp,
            UserStateSnapshot.user,
            UserStateSnapshot.health,
            UserStateSnapshot.collateralUsd,
            UserStateSnapshot.stablecoin,
            UserStateSnapshot.debt,
        )
        .join(Market, Market.id == UserStateSnapshot.marketId)
        .filter(func.lower(Market.id) == market_id.lower())
        .filter(UserStateSnapshot.timestamp == subquery)
    ).all()

    df = pd.DataFrame(
        query,
        columns=[
            "timestamp",
            "user",
            "health",
            "collateralUsd",
            "debt",
            "stablecoin",
        ],
    )

    try:
        bins = pd.qcut(df["health"], 10, retbins=True, duplicates="drop")[1]
    except ValueError:  # If there aren't enough unique values to create 10 deciles
        bins = pd.qcut(df["health"], 1, retbins=True, duplicates="drop")[1]

    labels = [
        "[{0:.5f}, {1:.5f})".format(bins[i], bins[i + 1])
        for i in range(len(bins) - 1)
    ]
    df["health_decile"] = pd.cut(
        df["health"], bins=bins, labels=labels, include_lowest=True
    )  # noqa

    sums_by_decile = (
        df.groupby("health_decile")[["collateralUsd", "stablecoin", "debt"]]
        .sum()
        .reset_index()
    )

    return [
        HealthDistribution(
            row["health_decile"],
            row["collateralUsd"],
            row["stablecoin"],
            row["debt"],
        )
        for _, row in sums_by_decile.iterrows()
    ]
