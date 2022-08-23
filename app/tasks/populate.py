from app import celery
from tasks.queries.curve.pools import get_curve_pools


@celery.task
def populate_db():
    get_curve_pools("mainnet")