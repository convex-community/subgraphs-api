from app import celery
from tasks.database.curve.snapshots import update_curve_pool_snapshots
from tasks.queries.curve.pools import get_curve_pools
from tasks.database.curve.pools import update_curve_pools
from celery.utils.log import get_task_logger

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
