from sqlalchemy.exc import SQLAlchemyError
from typing import List
from models.curve.snapshot import CurvePoolSnapshot, CurvePoolSnapshotSchema
from main import db
import logging

logger = logging.getLogger(__name__)


def update_curve_pool_snapshots(snapshots: List[CurvePoolSnapshot]):
    for snapshot in snapshots:
        db.session.merge(snapshot)
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error("Database error:", exc_info=e)
