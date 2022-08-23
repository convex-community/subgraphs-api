from app import celery
from tasks.queries.curve.pools import get_curve_pools
#from tasks.database.curve.pools import update_curve_pools
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@celery.task
def populate_curve_pools(chain):
    logger.info(f"Updating Curve Pools for {chain}")
    #update_curve_pools(get_curve_pools(chain))