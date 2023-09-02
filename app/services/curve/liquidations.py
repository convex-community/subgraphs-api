from sqlalchemy import func, text

from main import db
from models.curve.crvusd import (
    UserStateSnapshot,
    Market,
    MarketLosers,
    HistoricalMarketLosers,
    HistoricalMedianLoss,
    HistoricalSoftLoss,
    HealthDistribution,
    HistoricalLiquidations,
    AggregatedLiquidations,
    Liquidators,
    HistoricalHealth,
)
import pandas as pd
from web3 import Web3


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
    df["health_decile"] = pd.cut(  # noqa
        df["health"], bins=bins, labels=labels, include_lowest=True
    )

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


def get_liquidation_history(market_id):
    sql_query = """
        SELECT
            extract(epoch from date_trunc('day', to_timestamp("blockTimestamp")))::int AS "timestamp",
            SUM(CASE WHEN "user" = "liquidator" THEN 1 ELSE 0 END) AS "selfCount",
            SUM(CASE WHEN "user" != "liquidator" THEN 1 ELSE 0 END) AS "hardCount",
            SUM(CASE WHEN "user" = "liquidator" THEN "collateralReceivedUSD" + "stablecoinReceived" ELSE 0 END) AS "selfValue",
            SUM(CASE WHEN "user" != "liquidator" THEN "collateralReceivedUSD" + "stablecoinReceived" ELSE 0 END) AS "hardValue",
            AVG("oraclePrice") AS price
        FROM
            "liquidation"
        JOIN
            "market" ON "market"."id" = "liquidation"."marketId"
        WHERE
            LOWER("market"."id") = LOWER(:market_id)
        GROUP BY
            timestamp
        ORDER BY
            timestamp;
    """
    result = db.session.execute(text(sql_query), {"market_id": market_id})
    rows = result.fetchall()
    return [
        HistoricalLiquidations(
            timestamp=row[0],
            selfCount=row[1],
            hardCount=row[2],
            selfValue=row[3],
            hardValue=row[4],
            price=row[5],
        )
        for row in rows
    ]


def get_aggregated_liquidations(market_id):
    sql_query = """
        SELECT
            SUM(CASE WHEN "user" = "liquidator" THEN 1 ELSE 0 END) AS "selfCount",
            SUM(CASE WHEN "user" != "liquidator" THEN 1 ELSE 0 END) AS "hardCount",
            SUM(CASE WHEN "user" = "liquidator" THEN "collateralReceivedUSD" + "stablecoinReceived" ELSE 0 END) AS "selfValue",
            SUM(CASE WHEN "user" != "liquidator" THEN "collateralReceivedUSD" + "stablecoinReceived" ELSE 0 END) AS "hardValue"
        FROM
            "liquidation"
        WHERE
            LOWER("marketId") = LOWER(:market_id)
    """
    result = db.session.execute(text(sql_query), {"market_id": market_id})
    return AggregatedLiquidations(*result.fetchone())


def get_top_liquidators(market_id):
    sql_query = """
        SELECT
            "liquidator" AS "address",
            COUNT(*) AS "count",
            SUM("collateralReceivedUSD" + "stablecoinReceived") AS "value"
        FROM
            "liquidation"
        WHERE
            LOWER("marketId") = LOWER(:market_id) AND "user" != "liquidator"
        GROUP BY
            "liquidator"
        ORDER BY
            "count" DESC
        LIMIT 5
    """
    results = db.session.execute(text(sql_query), {"market_id": market_id})
    return [
        Liquidators(Web3.to_checksum_address(row[0]), row[1], row[2])
        for row in results
    ]


def get_historical_health(market_id):
    sql_query = """
WITH Top10Percent AS (
    SELECT "health"
    FROM "user_state_snapshots"
    WHERE LOWER("marketId") = LOWER(:market_id)
    ORDER BY "depositedCollateral" DESC
    LIMIT CAST(0.10 * (SELECT COUNT(*) FROM "user_state_snapshots" WHERE LOWER("marketId") = LOWER(:market_id)) AS INTEGER)
)
SELECT
    "timestamp",
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY "health") AS median_health,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY "health") AS median_health_for_top_10_percent
FROM
    "user_state_snapshots",
    Top10Percent
WHERE
    LOWER("marketId") = LOWER(:market_id)
GROUP BY
    "timestamp"
ORDER BY
    "timestamp";
    """

    result = db.session.execute(
        text(sql_query), {"market_id": market_id}
    ).fetchall()

    return [
        HistoricalHealth(
            timestamp=row[0],
            medianHealth=row[1],
            medianHealthTop10Percent=row[2],
            price=row[3],
        )
        for row in result
    ]
