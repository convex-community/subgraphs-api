import requests
import time
import pandas as pd
import numpy as np
import os
import json
from functools import reduce
from redis import Redis  # type: ignore
from main import db
from main.const import CHAIN_MAINNET, PoolType, CRVUSD_CONTRACT
from models.curve.pool import CurvePool
from tasks.queries.graph import grt_curve_pools_query
import logging


logger = logging.getLogger(__name__)

redis = Redis(
    host="redis", password=os.getenv("REDIS_PASSWORD", ""), port=6379, db=0
)

GRAPH_CRV_USD_PRICES_QUERY = """
{
  pool(id: "%s") {
    coinNames
  }
  swapEvents (orderBy:timestamp orderDirection: desc first: 1000 where: {pool: "%s" timestamp_lt: %s}) {
    tokenSold
    tokenBought
    amountSold
    amountBought
    amountSoldUSD
    amountBoughtUSD
    timestamp
  }
}
"""


def get_swaps(pool, days=30):
    now = int(time.time())
    current_time = now
    res = []
    while True:
        data = grt_curve_pools_query(
            CHAIN_MAINNET, GRAPH_CRV_USD_PRICES_QUERY % (pool, pool, now)
        )
        coin = [c for c in data["pool"]["coinNames"] if c != "crvUSD"][0]
        swaps = data["swapEvents"]
        if not swaps:
            logger.warning(f"Found no swaps at time {current_time} for {pool}")
            break
        last_timestamp = int(swaps[-1]["timestamp"])
        if last_timestamp == current_time:
            break
        current_time = last_timestamp
        res += swaps
        if last_timestamp < now - (days * 24 * 60 * 60):
            logger.warning(f"Went back more than {days} days for {pool}")
            break
    return coin, res


def get_prices(swaps):
    res = []
    for swap in swaps:
        if swap["tokenBought"] == CRVUSD_CONTRACT:
            price = float(swap["amountBought"]) / float(swap["amountSold"])
        else:
            price = float(swap["amountSold"]) / float(swap["amountBought"])
        res.append({"timestamp": swap["timestamp"], "price": price})
    return res


def get_crv_usd_pools():
    pools = (
        db.session.query(CurvePool)
        .with_entities(CurvePool.address)
        .filter(CurvePool.poolType == PoolType.CRVUSD.value)
        .all()
    )
    return [pool.address for pool in pools]


def get_cg_prices(days=30):
    r = requests.get(
        f"https://api.coingecko.com/api/v3/coins/crvusd/market_chart?vs_currency=usd&days={days}&interval=daily"
    )
    df = pd.DataFrame(r.json()["prices"])
    df.columns = ["timestamp", "USD"]
    df["timestamp"] = pd.to_datetime(df["timestamp"] / 1000, unit="s")
    df.set_index("timestamp", inplace=True)
    df_resampled = df.resample("D").mean()
    df_resampled.reset_index(inplace=True)
    return df_resampled


def get_crvusd_prices():
    pools = get_crv_usd_pools()
    res = {}
    for pool in pools:
        coin, swaps = get_swaps(pool, 30)
        swap_prices = get_prices(swaps)
        if not swap_prices:
            logger.info(f"No swaps for pool: {pool}")
            continue
        prices = pd.DataFrame(swap_prices)
        prices.columns = ["timestamp", coin]
        prices["timestamp"] = pd.to_datetime(
            prices["timestamp"].astype(int), unit="s"
        )
        prices.set_index("timestamp", inplace=True)
        prices_resampled = prices.resample("H").mean()
        prices_resampled.reset_index(inplace=True)
        res[coin] = prices_resampled
    crv_prices = reduce(
        lambda df1, df2: pd.merge(df1, df2, on="timestamp", how="outer"),
        res.values(),
    )
    crv_prices = crv_prices.fillna(method="ffill").fillna(method="bfill")

    cg_prices = get_cg_prices()
    final_df = crv_prices.copy()
    final_df["timestamp"] = final_df["timestamp"].apply(
        lambda x: int(x.timestamp())
    )
    res = final_df.to_dict(orient="records")

    redis.set("crvusd_prices", json.dumps(res))

    hist = np.histogram(cg_prices["USD"])
    hist = {"y": hist[0].tolist(), "x": hist[1].tolist()}

    redis.set("crvusd_hist", json.dumps(hist))
