from models.convex.pool import (
    ConvexPool,
    ConvexPoolName,
)
from main import db
from typing import List


def get_pool_names() -> List[ConvexPoolName]:
    return (
        db.session.query(ConvexPool.id, ConvexPool.name)
        .order_by(ConvexPool.id)
        .all()
    )


def get_all_pool_metadata() -> List[ConvexPool]:
    return db.session.query(ConvexPool).order_by(ConvexPool.id).all()


def get_pool_metadata(poolid: int) -> List[ConvexPool]:
    return (
        db.session.query(ConvexPool)
        .filter(ConvexPool.id == str(poolid))
        .order_by(ConvexPool.id)
        .all()
    )
