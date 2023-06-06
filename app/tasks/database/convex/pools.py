from models.convex.pool import ConvexPool
from typing import List
from main import db


def update_convex_pools(pools: List[ConvexPool]):
    try:
        for pool in pools:
            db.session.add(pool)
        db.session.commit()
    except Exception as e:
        print(f"Failed to add pools to database. Error: {e}")
        db.session.rollback()
