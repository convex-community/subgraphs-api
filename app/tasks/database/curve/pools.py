from sqlalchemy.exc import SQLAlchemyError
from typing import List
from main import db
from models.curve.pool import CurvePool
import logging

logger = logging.getLogger(__name__)


def update_curve_pools(pools: List[CurvePool]):
    for pool in pools:
        db.session.merge(pool)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error("Database error:", exc_info=e)
