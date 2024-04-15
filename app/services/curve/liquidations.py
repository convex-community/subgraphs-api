from sqlalchemy import func, text
from sqlalchemy.exc import SQLAlchemyError

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
    MarketHealthState,
    LiquidatorRevenue,
    CollateralRatios,
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
            "stablecoin",
            "debt",
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
WITH WeeklySnapshots AS (
    SELECT
        DATE_TRUNC('day', TO_TIMESTAMP("timestamp")) AS weekly_timestamp,
        "health"
    FROM
        "user_state_snapshots"
    WHERE
        LOWER("marketId") = LOWER(:market_id)
    AND
        "timestamp" >= EXTRACT(EPOCH FROM (NOW() - INTERVAL '6 months'))
),

IQRValues AS (
    SELECT
        weekly_timestamp,
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY "health") AS q1,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY "health") AS q3,
        PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY "health") -
        PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY "health") AS iqr
    FROM
        WeeklySnapshots
    GROUP BY
        weekly_timestamp
)

SELECT
    ws.weekly_timestamp,
    MIN(ws."health") AS min_health,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY ws."health") AS q1,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY ws."health") AS median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY ws."health") AS q3,
    MAX(ws."health") AS max_health
FROM
    WeeklySnapshots ws
JOIN
    IQRValues iqr ON ws.weekly_timestamp = iqr.weekly_timestamp
WHERE
    ws."health" <= iqr.q3 + 1.5 * iqr.iqr -- This filters out the high-end outliers
GROUP BY
    ws.weekly_timestamp
ORDER BY
    ws.weekly_timestamp;
"""

    result = db.session.execute(
        text(sql_query), {"market_id": market_id}
    ).fetchall()

    return [
        HistoricalHealth(
            timestamp=row[0].timestamp(),
            quartiles=[row[1], row[2], row[3], row[4], row[5]],
        )
        for row in result
    ]


def get_market_health(market_id):
    sql_query = """
    WITH RecentSnapshot AS (
        SELECT *
        FROM "user_states"
        WHERE LOWER("marketId") = LOWER(:market_id)
        AND "timestamp" = (SELECT MAX("timestamp") FROM "user_states" WHERE LOWER("marketId") = LOWER(:market_id))
    )

    SELECT
        SUM(CASE WHEN "softLiq" = TRUE THEN 1 ELSE 0 END) AS soft_liq_users,
        SUM(CASE WHEN "softLiq" = TRUE THEN 1 ELSE 0 END)::FLOAT / COUNT(*) AS soft_liq_ratio,
        SUM(CASE WHEN "health" < 0 THEN 1 ELSE 0 END) AS liqable_positions,
        SUM(CASE WHEN "health" < 0 THEN "debt" ELSE 0 END) AS liqable_debt,
        SUM(CASE WHEN "health" < 0 THEN "collateralUsd" ELSE 0 END) AS liqable_collat_usd,
        SUM(CASE WHEN "health" < 0 THEN "stableCoin" ELSE 0 END) AS liqable_stable,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY "health") AS median_health,
        SUM("collateralUsd") / NULLIF(SUM("debt" - "stableCoin"), 0) AS collat_ratio
    FROM RecentSnapshot;
    """

    result = db.session.execute(
        text(sql_query), {"market_id": market_id}
    ).fetchone()
    return MarketHealthState(*result)


def get_liquidator_revenue(market_id: str):
    sql_query = """
    WITH BonusCalculation AS (
        SELECT
            "blockTimestamp",
            SUM("collateralReceivedUSD" + "stablecoinReceived" - "debt") AS bonus_for_timestamp,
            1 - (SUM("debt") / SUM("collateralReceivedUSD" + "stablecoinReceived")) AS discount
        FROM
            "liquidation"
        WHERE
            LOWER("marketId") = LOWER(:market_id)
            AND "user" != "liquidator"
        GROUP BY
            "blockTimestamp"
    )
    SELECT
        "blockTimestamp",
        SUM(bonus_for_timestamp) OVER (ORDER BY "blockTimestamp") AS cumulative_bonus,
        AVG(discount) OVER (ORDER BY "blockTimestamp") AS discount
    FROM
        BonusCalculation
    ORDER BY
        "blockTimestamp";
    """
    results = db.session.execute(
        text(sql_query), {"market_id": market_id}
    ).fetchall()
    return [
        LiquidatorRevenue(
            timestamp=row[0], amount=float(row[1]), discount=float(row[2])
        )
        for row in results
    ]


def get_collateral_ratio(market_id: str):
    sql_query = """
    WITH OrderedResults AS (
        SELECT
            CAST("timestamp" / (24 * 60 * 60) AS INTEGER) * (24 * 60 * 60) AS day_timestamp,
            SUM("collateralUsd") / NULLIF(SUM("debt" - "stableCoin"), 0) AS CR
        FROM "user_states"
        WHERE LOWER("marketId") = LOWER(:market_id)
        GROUP BY day_timestamp
        ORDER BY day_timestamp DESC
    )
    SELECT day_timestamp, CR
    FROM OrderedResults;
    """
    try:
        results = db.session.execute(
            text(sql_query), {"market_id": market_id.lower()}
        ).fetchall()

        return [
            CollateralRatios(timestamp=row[0], ratio=float(row[1]))
            for row in results if row[1] is not None
        ]
    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")
        return []

