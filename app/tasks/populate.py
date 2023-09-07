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
from tasks.queries.curve.couch.couch import check_cushions
from tasks.queries.curve.crvusd.backfill import backfill
from tasks.queries.curve.crvusd.factory import update_stable_supply_data
from tasks.queries.curve.crvusd.health import update_user_states_and_health
from tasks.queries.curve.crvusd.keepers import update_keeper_debt_data
from tasks.queries.curve.crvusd.liquidations import (
    update_liquidation_data,
    update_user_liquidation_discounts,
)
from tasks.queries.curve.crvusd.markets import update_crvusd_market_data
from tasks.queries.curve.crvusd.prices import get_crvusd_prices
from tasks.queries.curve.crvusd.userstates import update_user_states
from tasks.queries.curve.decode_proposals import decode_proposals
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


@celery.task
def populate_crvusd_prices():
    logger.info(f"Updating crvUSD price Data")
    get_crvusd_prices()


@celery.task
def populate_crvusd_keeper_debt_data():
    logger.info(f"Updating crvUSD Keepers' historical debt data")
    update_keeper_debt_data()


@celery.task
def populate_crvusd_market_data():
    logger.info(f"Updating crvUSD market Data")
    update_crvusd_market_data()


@celery.task
def populate_couch_info():
    logger.info(f"Updating Curve Couch Info")
    check_cushions()


@celery.task
def populate_user_states():
    logger.info(f"Updating User States")
    update_user_states_and_health()


@celery.task
def populate_dao_decoded_proposal_data():
    logger.info(f"Updating decoded dao proposal data")
    decode_proposals()


@celery.task
def populate_user_state_snapshots():
    logger.info(f"Updating user state snapshot data")
    update_user_states()


@celery.task
def populate_liquidations():
    logger.info(f"Updating liquidation data")
    update_liquidation_data()
    update_user_liquidation_discounts()


@celery.task
def populate_supply_events():
    logger.info(f"Updating stablecoin supply data")
    update_stable_supply_data()


@celery.task
def populate_backfill():
    logger.info(f"Running backfill script")
    backfill()
