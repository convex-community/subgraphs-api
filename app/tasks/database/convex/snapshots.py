from models.convex.snapshot import ConvexPoolSnapshot, ConvexPoolSnapshotSchema
from sqlalchemy.exc import SQLAlchemyError
from main import db
from typing import List
import math
import logging

logger = logging.getLogger(__name__)


def update_convex_pool_snapshots(pools: List[ConvexPoolSnapshot]):
    for pool in pools:
        base_apr = pool.baseApr if pool.baseApr is not None else None
        if base_apr is None or math.isnan(base_apr) or math.isinf(base_apr):
            logger.error(f"Invalid or inexistant value for baseApr in {pool}")
            continue
        db.session.merge(pool)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error("Database error:", exc_info=e)
