from decimal import Decimal

from main.const import DAY
from models.curve.returns import (
    CurvePoolIlCalcDataSchema,
    ConvexAprDataSchema,
    ConvexAprData,
    CurvePoolIlCalcData,
    LpHodlXyk,
    CurveReturnSeries,
    CurveReturnSeriesSchema,
)
from services.query import query_db, get_container
from typing import List, Union, Optional
from marshmallow import EXCLUDE
import pandas as pd
import numpy as np


def _exec_curve_query(query: str) -> List:
    return query_db(get_container("CurvePoolSnapshots"), query)


def _exec_convex_query(query: str) -> List:
    return query_db(get_container("ConvexPoolSnapshots"), query)


def _get_curve_base_data(
    end_date: int, start_date: int, chain: str, pool: str
) -> List[CurvePoolIlCalcData]:
    query = f"SELECT c.lpPriceUSD, c.normalizedReserves, c.reservesUSD, c.tvl, c.timestamp FROM CurvePoolSnapshots as c WHERE c.chain = '{chain}' AND c.pool = '{pool}' AND c.timestamp <= { end_date } AND c.timestamp >= { start_date } ORDER BY c.timestamp ASC"
    return CurvePoolIlCalcDataSchema(many=True).load(
        _exec_curve_query(query), unknown=EXCLUDE
    )


def _get_convex_apr_data(
    end_date: int, start_date: int, pool: str
) -> List[ConvexAprData]:
    query = f"SELECT c.crvApr, c.cvxApr, c.timestamp FROM ConvexPoolSnapshots as c WHERE c.swap = '{pool}' AND c.timestamp <= { end_date } AND c.timestamp >= { start_date } ORDER BY c.timestamp ASC"
    return ConvexAprDataSchema(many=True).load(
        _exec_convex_query(query), unknown=EXCLUDE
    )


def gmean(x: List[Union[float, int]]):
    """
    Compute geometric mean of a series
    """
    a = np.log(x)
    return np.exp(a.mean())


def _get_prices(snapshot: CurvePoolIlCalcData) -> List[float]:
    """
    Subgraph does not store the token prices directly
    We infer them back from usd denom reserves / token denom reserves
    :param snapshot: pool snapshot
    :return: list of pool's tokens' prices in USD
    """
    return [
        r_usd / ((snapshot.normalizedReserves[i]) * 1e-18)
        for i, r_usd in enumerate(snapshot.reservesUSD)
    ]


def _calc_hodl_ratios(snapshot: CurvePoolIlCalcData) -> List[float]:
    """
    Give us proportion of each token in pool based on reserves to
    estimate HODL ratio at time when someone enters the pool
    :param snapshot: pool snapshot
    :return: proportion of each token in pool
    """
    supply = snapshot.tvl / snapshot.lpPriceUSD  # lptoken supply
    return [(r * 1e-18) / supply for r in snapshot.normalizedReserves]


def compute_series(snapshots: List[CurvePoolIlCalcData]) -> List[LpHodlXyk]:
    """
    Generate historical usd values for:
     - curve lp token price,
     - hodl position opened at same date
     - 0 fee xyk amm position opened at same date
    :param snapshots: list of pool snapshots
    :return: historical values for curve, hodl & xyk series
    """
    res = []
    # remove null data
    snapshots = [
        s
        for s in snapshots
        if not (s.tvl == 0 or s.lpPriceUSD == 0 or 0 in s.reservesUSD)
    ]
    original_data = snapshots[0]
    original_prices = _get_prices(original_data)
    hodl_ratios = _calc_hodl_ratios(original_data)
    for snapshot in snapshots:
        prices = _get_prices(snapshot)
        hodl_value = sum(
            ratio * prices[i] for i, ratio in enumerate(hodl_ratios)
        )
        # account for 3+ token pools in xyk
        price_ratios = [
            (price / prices[0]) / (original_prices[i] / original_prices[0])
            for i, price in enumerate(prices)
        ]
        impermanent_loss = gmean(price_ratios) / np.mean(price_ratios)
        xyk_value = hodl_value * impermanent_loss
        res.append(
            LpHodlXyk(
                snapshot.lpPriceUSD, hodl_value, xyk_value, snapshot.timestamp
            )
        )
    return res


def get_returns(
    chain: str, pool: str, start_date: int, end_date: int, lp_tokens: str
) -> Optional[CurveReturnSeries]:

    curve_data = _get_curve_base_data(end_date, start_date, chain, pool)
    convex_data = _get_convex_apr_data(end_date, start_date, pool)

    if not (curve_data and convex_data):
        return None
    lp_prices = compute_series(curve_data)
    lp_df = pd.DataFrame(lp_prices)
    ret_df = pd.DataFrame(convex_data)
    # ensure timestamps have similar rounding
    ret_df["timestamp"] = ret_df["timestamp"] // DAY * DAY
    lp_df["timestamp"] = lp_df["timestamp"] // DAY * DAY
    lp_token_amount = Decimal(lp_tokens) * Decimal(1e-18)
    # series have been calculated for one unit of lp token
    lp_df[["curve", "hodl", "xyk"]] = lp_df[["curve", "hodl", "xyk"]] * float(
        lp_token_amount
    )
    lp_df.set_index("timestamp", inplace=True)
    ret_df.set_index("timestamp", inplace=True)
    rewards_df = lp_df.join(ret_df, how="inner")
    rewards_df["crvReturns"] = (
        lp_df["curve"] * (ret_df["crvApr"] / 365)
    ).cumsum()
    rewards_df["cvxReturns"] = (
        lp_df["curve"] * (ret_df["cvxApr"] / 365)
    ).cumsum()
    rewards_df["inclRewards"] = (
        rewards_df["curve"]
        + rewards_df["cvxReturns"]
        + rewards_df["crvReturns"]
    )

    # compute differentials as they're easier to visualize
    final_df = pd.DataFrame()
    final_df["curve"] = rewards_df["curve"] - rewards_df["hodl"]
    final_df["xyk"] = rewards_df["xyk"] - rewards_df["hodl"]
    final_df["curve_rewards"] = rewards_df["inclRewards"] - rewards_df["hodl"]
    final_df["hodl"] = 0
    final_df["timestamp"] = rewards_df.index

    data = final_df.reset_index(drop=True).to_dict("records")
    return CurveReturnSeriesSchema(many=True).load(data, unknown=EXCLUDE)
