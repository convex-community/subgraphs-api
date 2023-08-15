from operator import not_

from main import db
from sqlalchemy import func, and_, cast, Date, any_
import time
import os
from redis import Redis  # type: ignore
import pandas as pd
import json
from celery.utils.log import get_task_logger

from main.const import CHAINS, BLACKLIST
from models.curve.pool import CurvePool
from models.curve.snapshot import CurvePoolSnapshot
from tasks.queries.graph import grt_curve_pools_query
from utils import shortify_pool_name

"""
This is used to generate the rankings for the landing page
We simply store the outcomes in redis
"""
redis = Redis(
    host="redis", password=os.getenv("REDIS_PASSWORD", ""), port=6379, db=0
)

pd.options.mode.chained_assignment = None
blacklist_filter = ~(func.lower(CurvePoolSnapshot.pool).in_(BLACKLIST.keys()))

DAY = 24 * 60 * 60
logger = get_task_logger(__name__)


def get_tvl_gainers_losers():
    logger.info("Getting largest TVL gains & losses")
    today = (time.time() // DAY) * DAY - DAY
    yesterday = today - DAY

    today_tvl_query = (
        db.session.query(
            CurvePoolSnapshot.pool,
            CurvePoolSnapshot.chain,
            CurvePool.name,
            CurvePoolSnapshot.tvl,
        )
        .join(
            CurvePool,
            and_(
                CurvePoolSnapshot.pool == CurvePool.address,
                CurvePoolSnapshot.chain == CurvePool.chain,
            ),
        )
        .filter(
            and_(
                CurvePoolSnapshot.timestamp >= today,
                CurvePoolSnapshot.timestamp < today + DAY,
            )
        )
        .filter(blacklist_filter)
        .all()
    )

    yesterday_tvl_query = (
        db.session.query(
            CurvePoolSnapshot.pool,
            CurvePoolSnapshot.chain,
            CurvePoolSnapshot.tvl,
        )
        .join(
            CurvePool,
            and_(
                CurvePoolSnapshot.pool == CurvePool.address,
                CurvePoolSnapshot.chain == CurvePool.chain,
            ),
        )
        .filter(
            and_(
                CurvePoolSnapshot.timestamp >= yesterday,
                CurvePoolSnapshot.timestamp < yesterday + DAY,
            )
        )
        .filter(blacklist_filter)
        .all()
    )
    if len(today_tvl_query) < 1 or len(yesterday_tvl_query) < 1:
        # on first init we won't have snapshots
        return

    td = pd.DataFrame(today_tvl_query)
    yd = pd.DataFrame(yesterday_tvl_query)

    df = pd.merge(
        yd, td, on=["pool", "chain"], suffixes=["_yesterday", "_today"]
    )
    # filter no value pools
    threshold = 50000
    df = df[(df["tvl_yesterday"] > 0) & (df["tvl_today"] > threshold)]
    df["tvl_growth"] = (
        (df["tvl_today"] - df["tvl_yesterday"]) / df["tvl_yesterday"] * 100
    )
    df["name"] = df["name"].apply(shortify_pool_name)

    losers = df.sort_values("tvl_growth")[:10][
        ["pool", "chain", "name", "tvl_growth"]
    ].to_dict(orient="records")
    gainers = df.sort_values("tvl_growth", ascending=False)[:10][
        ["pool", "chain", "name", "tvl_growth"]
    ].to_dict(orient="records")
    redis.set("tvl_losers", json.dumps(losers))
    redis.set("tvl_gainers", json.dumps(gainers))


def get_top_vol_tvl_utilization():
    logger.info("Getting volumes & tvl stats by chain & pool types")
    today = int((time.time() // DAY) * DAY - DAY)
    query = (
        db.session.query(
            CurvePoolSnapshot.pool,
            CurvePoolSnapshot.chain,
            CurvePoolSnapshot.volumeUSD,
            CurvePoolSnapshot.tvl,
            CurvePool.isV2,
            CurvePool.name,
            CurvePool.assetType,
            CurvePool.poolType,
        )
        .join(
            CurvePool,
            and_(
                CurvePoolSnapshot.pool == CurvePool.address,
                CurvePoolSnapshot.chain == CurvePool.chain,
            ),
        )
        .filter(CurvePoolSnapshot.timestamp == today)
        .filter(blacklist_filter)
        .all()
    )
    if len(query) < 1:
        return

    df = pd.DataFrame(query)
    df["name"] = df["name"].apply(shortify_pool_name)

    def label_pool(row):
        if row["isV2"]:
            return "V2"
        elif row["poolType"] == "CRVUSD":
            return "CRVUSD"
        elif row["assetType"] == 0:
            return "V1-USD"
        elif row["assetType"] == 1:
            return "V1-ETH"
        elif row["assetType"] == 2:
            return "V1-BTC"
        else:
            return "V1-OTHER"

    df["type"] = df[["isV2", "poolType", "assetType"]].apply(
        label_pool, axis=1
    )
    volume_breakdown = (
        df[["chain", "volumeUSD"]]
        .groupby("chain")
        .sum()
        .reset_index()
        .to_dict(orient="records")
    )

    tvl_breakdown = (
        df[["chain", "tvl"]]
        .groupby("chain")
        .sum()
        .reset_index()
        .to_dict(orient="records")
    )
    redis.set("volume_breakdown_chain", json.dumps(volume_breakdown))
    redis.set("tvl_breakdown_chain", json.dumps(tvl_breakdown))

    volume_breakdown = (
        df[["type", "volumeUSD"]]
        .groupby("type")
        .sum()
        .reset_index()
        .to_dict(orient="records")
    )
    tvl_breakdown = (
        df[["type", "tvl"]]
        .groupby("type")
        .sum()
        .reset_index()
        .to_dict(orient="records")
    )
    redis.set("volume_breakdown_type", json.dumps(volume_breakdown))
    redis.set("tvl_breakdown_type", json.dumps(tvl_breakdown))

    df = df[(df["volumeUSD"] > 50000) & (df["tvl"] > 100000)]
    df["liq_use"] = df["volumeUSD"] / df["tvl"]
    big_users = df.sort_values("liq_use", ascending=False)[:10][
        ["pool", "chain", "name", "liq_use"]
    ].to_dict(orient="records")
    redis.set("big_users", json.dumps(big_users))


def get_sizeable_trades():
    logger.info("Getting latest sizeable trades")
    today = int((time.time() // DAY) * DAY - DAY)
    QUERY = """
    {
      swapEvents(where:{timestamp_gt: %d} orderBy: amountSoldUSD orderDirection: desc first: 10) {
        tx
        amountSoldUSD
        pool {
          address
          name
        }
      }
    }
    """
    graph_query = QUERY % today
    all_swaps = []
    for chain in CHAINS:
        data = grt_curve_pools_query(chain, graph_query)
        swaps = [
            {
                "tx": d["tx"],
                "value": d["amountSoldUSD"],
                "chain": chain,
                "pool": d["pool"]["address"],
                "name": d["pool"]["name"],
            }
            for d in data["swapEvents"]
        ]
        all_swaps += swaps
    df = pd.DataFrame(all_swaps)
    df["value"] = df["value"].astype(float)
    trades = df.sort_values("value", ascending=False)[:50].to_dict(
        orient="records"
    )
    redis.set("sizeable_trades", json.dumps(trades))
