from main.const import WEEK, DAY
from models.curve.revenue import (
    CurvePoolRevenue,
    CurvePoolRevenueSchema,
    CurveChainRevenue,
    CurveChainRevenueSchema,
    CurveHistoricalPoolCumulativeRevenueSchema,
    CurveHistoricalPoolCumulativeRevenue,
    CurveChainTopPoolRevenue,
    CurveChainTopPoolRevenueSchema,
)
from services.curve.pool import get_all_pool_names
from services.query import query_db, get_container
from typing import List, Mapping, Union
from marshmallow import EXCLUDE
import pandas as pd
from datetime import datetime


def _exec_query(query: str) -> List:
    return query_db(get_container("CurvePoolSnapshots"), query)


def _get_all_revenue_snapshots() -> List[CurvePoolRevenue]:
    query = f"SELECT c.totalDailyFeesUSD, c.pool, c.timestamp, c.chain FROM CurvePoolSnapshots as c"
    return CurvePoolRevenueSchema(many=True).load(
        _exec_query(query), unknown=EXCLUDE
    )


def _get_all_revenue_snapshots_last_week(chain) -> List[CurvePoolRevenue]:
    start_date = (int(datetime.now().timestamp() // DAY) * DAY) - WEEK
    query = f"SELECT c.totalDailyFeesUSD, c.pool, c.timestamp, c.chain FROM CurvePoolSnapshots as c WHERE c.chain = '{chain}' AND c.timestamp >= {start_date}"
    return CurvePoolRevenueSchema(many=True).load(
        _exec_query(query), unknown=EXCLUDE
    )


def get_top_chain_pools(
    chain: str, top: int
) -> List[CurveChainTopPoolRevenue]:
    df_rev = pd.DataFrame(_get_all_revenue_snapshots_last_week(chain))
    df_names = pd.DataFrame(get_all_pool_names())
    df_names["name"] = df_names["name"].apply(
        lambda x: str(x).replace("Curve.fi", "").split(":")[-1]
    )
    df = pd.merge(
        df_rev,
        df_names,
        left_on=["pool", "chain"],
        right_on=["address", "chain"],
        how="left",
    ).drop(columns=["address"])
    top_performers = (
        df[["name", "totalDailyFeesUSD"]]
        .groupby("name")
        .sum()
        .sort_values(by="totalDailyFeesUSD", ascending=False)[:top]
    )
    data: List[Mapping[str, Union[str, float]]] = top_performers.reset_index().to_dict(orient="records")  # type: ignore
    return CurveChainTopPoolRevenueSchema(many=True).load(
        data, unknown=EXCLUDE
    )


def get_top_pools(top: int) -> List[CurveHistoricalPoolCumulativeRevenue]:
    df_rev = pd.DataFrame(_get_all_revenue_snapshots())
    df_names = pd.DataFrame(get_all_pool_names())
    df_names["name"] = (
        df_names["name"].apply(
            lambda x: str(x).replace("Curve.fi", "").split(":")[-1]
        )
        + " ("
        + df_names["chain"]
        + ")"
    )
    df = pd.merge(
        df_rev,
        df_names,
        left_on=["pool", "chain"],
        right_on=["address", "chain"],
        how="left",
    ).drop(columns=["address"])
    df = df.sort_values("timestamp", ascending=True)
    top_performers = (
        df[["totalDailyFeesUSD", "name"]]
        .groupby("name")
        .sum()
        .sort_values(by="totalDailyFeesUSD", ascending=False)
        .index[:top]
    )
    df["name"] = df["name"].apply(
        lambda x: x if x in top_performers else "Others"
    )
    df["timestamp"] = df["timestamp"].apply(
        lambda x: ((int(x) // WEEK) * WEEK)
    )
    df = (
        df[["totalDailyFeesUSD", "name", "timestamp"]]
        .groupby(["name", "timestamp"])
        .sum()
        .reset_index()
    )
    df["cumulativeDailyFeesUSD"] = (
        df["totalDailyFeesUSD"].groupby(df["name"]).cumsum()
    )
    df = (
        df[["name", "timestamp", "cumulativeDailyFeesUSD"]]
        .pivot_table("cumulativeDailyFeesUSD", ["name"], "timestamp")
        .fillna(0)
        .transpose()
        .reset_index()
    )
    data: List[Mapping[str, Union[str, int, float]]] = df.melt(  # type: ignore
        id_vars=["timestamp"], var_name="pool", value_name="revenue"
    ).to_dict("records")
    return CurveHistoricalPoolCumulativeRevenueSchema(many=True).load(
        data, unknown=EXCLUDE
    )


def get_platform_revenue() -> List[CurveChainRevenue]:
    df_rev = pd.DataFrame(_get_all_revenue_snapshots())
    data = (
        df_rev[["totalDailyFeesUSD", "chain"]]
        .groupby("chain")
        .sum()
        .reset_index()
        .to_dict(orient="records")
    )
    return CurveChainRevenueSchema(many=True).load(data, unknown=EXCLUDE)
