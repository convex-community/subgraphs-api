from sqlalchemy import func

from main.const import WEEK, DAY, BLACKLIST
from models.curve.pool import CurvePool
from models.curve.revenue import (
    CurvePoolRevenue,
    CurvePoolRevenueSchema,
    CurveChainRevenue,
    CurveChainRevenueSchema,
    CurveHistoricalPoolCumulativeRevenueSchema,
    CurveHistoricalPoolCumulativeRevenue,
    CurveChainTopPoolRevenue,
    CurveChainTopPoolRevenueSchema,
    CouchInfo,
)
from main import db
from models.curve.snapshot import CurvePoolSnapshot
from services.curve.pool import get_all_pool_names
from typing import List, Mapping, Union
from marshmallow import EXCLUDE
import pandas as pd
from datetime import datetime

blacklist_filter = ~(func.lower(CurvePoolSnapshot.pool).in_(BLACKLIST.keys()))


def _get_all_revenue_snapshots() -> List[CurvePoolRevenue]:
    # we end 48h before because there are differences between the times
    # each subgraphs take snapshots
    end_date = (int(datetime.now().timestamp() // DAY) * DAY) - DAY
    result = (
        db.session.query(
            CurvePoolSnapshot.totalDailyFeesUSD,
            CurvePoolSnapshot.pool,
            CurvePoolSnapshot.timestamp,
            CurvePoolSnapshot.chain,
        )
        .filter(CurvePoolSnapshot.timestamp < end_date)
        .filter(blacklist_filter)
        .all()
    )
    result = [CurvePoolRevenueSchema().load(row._asdict()) for row in result]
    return result


def _get_pool_revenue_snapshots(
    chain: str, pool: str
) -> List[CurvePoolRevenue]:
    base_query = db.session.query(
        CurvePoolSnapshot.totalDailyFeesUSD,
        CurvePoolSnapshot.pool,
        CurvePoolSnapshot.timestamp,
        CurvePoolSnapshot.chain,
    )
    result = base_query.filter(
        CurvePoolSnapshot.chain == chain, CurvePoolSnapshot.pool == pool
    ).all()

    if pool.lower() in map(str.lower, BLACKLIST.keys()):
        blacklist_timestamp = BLACKLIST[pool.lower()]
        for row in result:
            if row.timestamp > blacklist_timestamp:
                row.totalDailyFeesUSD = 0
    result = [CurvePoolRevenueSchema().load(row._asdict()) for row in result]
    return result


def _get_all_revenue_snapshots_last_week(chain: str) -> List[CurvePoolRevenue]:
    start_date = (int(datetime.now().timestamp() // DAY) * DAY) - WEEK
    result = (
        db.session.query(
            CurvePoolSnapshot.totalDailyFeesUSD,
            CurvePoolSnapshot.pool,
            CurvePoolSnapshot.timestamp,
            CurvePoolSnapshot.chain,
        )
        .filter(
            CurvePoolSnapshot.chain == chain,
            CurvePoolSnapshot.timestamp >= start_date,
        )
        .filter(blacklist_filter)
        .all()
    )
    result = [CurvePoolRevenueSchema().load(row._asdict()) for row in result]
    return result


def _merge_rev_and_names(
    df_names: pd.DataFrame, df_rev: pd.DataFrame
) -> pd.DataFrame:
    return pd.merge(
        df_rev,
        df_names,
        left_on=["pool", "chain"],
        right_on=["address", "chain"],
        how="left",
    ).drop(columns=["address"])


def get_top_chain_pools(
    chain: str, top: int
) -> List[CurveChainTopPoolRevenue]:
    df_rev = pd.DataFrame(_get_all_revenue_snapshots_last_week(chain))
    df_names = pd.DataFrame(get_all_pool_names())
    df_names["name"] = df_names["name"].apply(
        lambda x: str(x).replace("Curve.fi", "").split(":")[-1].strip()
    )
    df = _merge_rev_and_names(df_names, df_rev)
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
            lambda x: str(x).replace("Curve.fi", "").split(":")[-1].strip()
        )
        + " ("
        + df_names["chain"]
        + ")"
    )
    df = _merge_rev_and_names(df_names, df_rev)
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


def get_pool_revenue(chain: str, pool: str) -> List[CurvePoolRevenue]:
    return _get_pool_revenue_snapshots(chain, pool)


def check_couch_cushion() -> List[dict]:
    results = (
        db.session.query(
            CurvePool.address,
            CurvePool.name,
            CurvePool.coins,
            CurvePool.coinNames,
            CurvePool.isV2,
            CurvePool.id,
            CouchInfo.balance,
            CouchInfo.value,
            CouchInfo.totalUSD,
        )
        .join(CouchInfo, CurvePool.id == CouchInfo.poolId)
        .order_by(CouchInfo.totalUSD.desc())
        .all()
    )

    return [
        {
            "pool": r.name,
            "address": r.address,
            "chain": r.id.split("-")[-1],
            "coins": r.coins,
            "coinNames": r.coinNames if not r.isV2 else ["LP Token"],
            "balance": r.balance,
            "value": r.value,
            "totalUSD": r.totalUSD,
        }
        for r in results
    ]
