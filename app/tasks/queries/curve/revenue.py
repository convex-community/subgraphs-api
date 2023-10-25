import os
import time
import json
import pandas as pd
from redis import Redis  # type: ignore
from sqlalchemy import func, literal, case

from main.const import WEEK, BLACKLIST
from models.curve.crvusd import CollectedFees, Market
from main import db
from models.curve.snapshot import CurvePoolSnapshot
import logging

from services.curve.revenue import _get_all_revenue_snapshots

logger = logging.getLogger(__name__)
blacklist_filter = ~(func.lower(CurvePoolSnapshot.pool).in_(BLACKLIST.keys()))


redis = Redis(
    host="redis", password=os.getenv("REDIS_PASSWORD", ""), port=6379, db=0
)


def get_historical_fee_breakdown():
    start = int(time.time() - (WEEK * 26))
    logger.warning("Getting historical fee breakdown")
    crvusd_fees = (
        db.session.query(
            func.sum(
                func.coalesce(CollectedFees.ammCollateralFeesUsd, 0)
                + func.coalesce(CollectedFees.ammBorrowingFees, 0)
                + func.coalesce(CollectedFees.borrowingFees, 0)
            ).label("total_fees"),
            (CollectedFees.blockTimestamp // WEEK * WEEK).label("week"),
            case(
                (Market.chain == "mainnet", literal("crvusd-mainnet")),
                else_=literal("crvusd-alt_chains"),
            ).label("label"),
        )
        .join(Market, Market.id == CollectedFees.marketId)
        .filter((CollectedFees.blockTimestamp // WEEK * WEEK) >= start)
        .group_by("week", "label")
    )

    pools_fees_admin = (
        db.session.query(
            func.sum(
                CurvePoolSnapshot.totalDailyFeesUSD
                * CurvePoolSnapshot.adminFee
            ).label("total_fees"),
            (CurvePoolSnapshot.timestamp // WEEK * WEEK).label("week"),
            case(
                (
                    CurvePoolSnapshot.chain == "mainnet",
                    literal("pools-admin-mainnet"),
                ),
                else_=literal("pools-admin-alt_chains"),
            ).label("label"),
        )
        .filter(CurvePoolSnapshot.totalDailyFeesUSD < 1e7)
        .filter(~CurvePoolSnapshot.pool.in_(BLACKLIST.keys()))
        .filter((CurvePoolSnapshot.timestamp // WEEK * WEEK) >= start)
        .group_by("week", "label")
    )

    pools_fees_lp = (
        db.session.query(
            func.sum(
                CurvePoolSnapshot.totalDailyFeesUSD
                * (1 - CurvePoolSnapshot.adminFee)
            ).label("total_fees"),
            (CurvePoolSnapshot.timestamp // WEEK * WEEK).label("week"),
            case(
                (
                    CurvePoolSnapshot.chain == "mainnet",
                    literal("pools-lp-mainnet"),
                ),
                else_=literal("pools-lp-alt_chains"),
            ).label("label"),
        )
        .filter(CurvePoolSnapshot.totalDailyFeesUSD < 1e7)
        .filter(~CurvePoolSnapshot.pool.in_(BLACKLIST.keys()))
        .filter((CurvePoolSnapshot.timestamp // WEEK * WEEK) >= start)
        .group_by("week", "label")
    )

    crvusd_fees_results = crvusd_fees.all()
    pools_fees_admin_results = pools_fees_admin.all()
    pools_fees_lp_results = pools_fees_lp.all()
    results = (
        crvusd_fees_results + pools_fees_admin_results + pools_fees_lp_results
    )

    weekly_fees = [
        {"week": r[1], "label": r[2], "total_fees": r[0]} for r in results
    ]
    sorted_weekly_fees = sorted(
        weekly_fees, key=lambda x: (-x["week"], x["label"])
    )

    redis.set("historical_fee_breakdown", json.dumps(sorted_weekly_fees))


def get_platform_revenue():
    df_rev = pd.DataFrame(_get_all_revenue_snapshots())
    data = (
        df_rev[["totalDailyFeesUSD", "chain"]]
        .groupby("chain")
        .sum()
        .reset_index()
        .to_dict(orient="records")
    )
    redis.set("platform_revenue", json.dumps(data))
