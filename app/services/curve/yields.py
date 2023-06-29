from operator import and_
from typing import List
import requests
from sqlalchemy import func
import logging
from main import db
from models.convex.snapshot import ConvexPoolSnapshot
from models.curve.crvusd import CrvUsdYield

logger = logging.getLogger(__name__)


def get_latest_convex_pool_apr() -> List:
    subquery = (
        db.session.query(
            ConvexPoolSnapshot.poolName,
            func.max(ConvexPoolSnapshot.timestamp).label("max_timestamp"),
        )
        .filter(
            ConvexPoolSnapshot.poolName.ilike(
                "%Curve.fi Factory Plain Pool: crvUSD%"
            )
        )
        .group_by(ConvexPoolSnapshot.poolName)
        .subquery()
    )

    result = (
        db.session.query(
            ConvexPoolSnapshot.baseApr,
            ConvexPoolSnapshot.crvApr,
            ConvexPoolSnapshot.cvxApr,
            ConvexPoolSnapshot.extraRewardsApr,
            ConvexPoolSnapshot.timestamp,
            ConvexPoolSnapshot.poolName,
        )
        .join(
            subquery,
            and_(
                ConvexPoolSnapshot.poolName == subquery.c.poolName,
                ConvexPoolSnapshot.timestamp == subquery.c.max_timestamp,
            ),
        )
        .all()
    )

    return [
        CrvUsdYield(
            platform="Convex", pool=r[5], apy=(r[0] + r[1] + r[2] + r[3]) * 100
        )
        for r in result
    ]


def get_max_boost_curve_yield() -> List[CrvUsdYield]:
    CURVE_APR = "https://www.convexfinance.com/api/curve-apys"
    r = requests.get(CURVE_APR)
    return [
        CrvUsdYield(
            platform="Curve (max boost)",
            pool=k,
            apy=v["crvApy"] + v["baseApy"],
        )
        for k, v in r.json()["apys"].items()
        if "factory-crvusd" in k
    ]


def get_conic_omnipool() -> List[CrvUsdYield]:
    CNC_YIELD = (
        "https://yields.llama.fi/chart/69a83093-60c1-42ad-9927-2bc85b3dabe8"
    )
    r = requests.get(CNC_YIELD)
    return [
        CrvUsdYield(
            platform="Conic",
            pool="crvUSD omnipool",
            apy=r.json()["data"][-1]["apy"],
        )
    ]


def get_std_yields() -> List[CrvUsdYield]:
    STD_YIELD = "https://lockers.stakedao.org/api/strategies/cache/curve"
    r = requests.get(STD_YIELD)
    yields = {
        a["name"]: sum([b["apr"] for b in a["aprBreakdown"]]) * 100
        for a in r.json()
        if "crvusd" in a["key"]
    }
    return [
        CrvUsdYield(platform="StakeDAO", pool=k, apy=v)
        for k, v in yields.items()
    ]


def get_crv_usd_yields() -> List[CrvUsdYield]:
    try:
        convex_yields = get_latest_convex_pool_apr()
    except Exception as e:
        logger.error(f"Error fetching Convex yields : {e}")
        convex_yields = []
    try:
        curve_yields = get_max_boost_curve_yield()
    except Exception as e:
        logger.error(f"Error fetching Curve yields : {e}")
        curve_yields = []
    try:
        conic_yields = get_conic_omnipool()
    except Exception as e:
        logger.error(f"Error fetching Conic yields : {e}")
        conic_yields = []
    try:
        std_yields = get_std_yields()
    except Exception as e:
        logger.error(f"Error fetching StakeDAO yields : {e}")
        std_yields = []

    return conic_yields + convex_yields + curve_yields + std_yields
