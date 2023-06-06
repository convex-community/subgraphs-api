from app import celery
from tasks.database.convex.pools import update_convex_pools
from tasks.database.convex.revenue import (
    update_convex_revenue_snapshots,
    update_convex_cumulative_revenue,
)
from tasks.database.convex.snapshots import update_convex_pool_snapshots
from tasks.database.curve.snapshots import update_curve_pool_snapshots
from tasks.queries.convex.pools import get_convex_pools
from tasks.queries.convex.revenue import (
    get_convex_revenue_snapshots,
    get_convex_cumulative_revenue,
)
from tasks.queries.convex.snapshots import get_convex_pool_snapshots
from tasks.queries.curve.pools import get_curve_pools
from tasks.database.curve.pools import update_curve_pools
from celery.utils.log import get_task_logger

from tasks.queries.curve.rankings import (
    get_tvl_gainers_losers,
    get_top_vol_tvl_utilization,
    get_sizeable_trades,
)
from tasks.queries.curve.snapshots import get_curve_pool_snapshots

logger = get_task_logger(__name__)


@celery.task
def populate_curve_pools(chain):
    logger.info(f"Updating Curve Pools for {chain}")
    update_curve_pools(get_curve_pools(chain))


@celery.task
def populate_curve_pool_snapshots(chain):
    logger.info(f"Updating Curve Pool Snapshots for {chain}")
    update_curve_pool_snapshots(get_curve_pool_snapshots(chain))


@celery.task
def populate_convex_pools():
    logger.info(f"Updating Convex Pools")
    update_convex_pools(get_convex_pools())


@celery.task
def populate_convex_pool_snapshots():
    logger.info(f"Updating Convex Pool Snapshots")
    update_convex_pool_snapshots(get_convex_pool_snapshots())


@celery.task
def populate_convex_revenue_snapshots():
    logger.info(f"Updating Convex Revenue Snapshots")
    update_convex_revenue_snapshots(get_convex_revenue_snapshots())


@celery.task
def populate_convex_cumulative_revenue():
    logger.info(f"Updating Convex Cumulative Revenue Data")
    update_convex_cumulative_revenue(get_convex_cumulative_revenue())


@celery.task
def populate_daily_rankings():
    logger.info(f"Updating Daily Ranking Data")
    get_tvl_gainers_losers()
    get_top_vol_tvl_utilization()


@celery.task
def populate_hourly_rankings():
    logger.info(f"Updating Hourly Ranking Data")
    get_sizeable_trades()
