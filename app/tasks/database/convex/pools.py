from models.convex.pool import ConvexPool, ConvexPoolSchema
from tasks.database.client import get_container
from typing import List
from main import db

CONTAINER_NAME = "ConvexPools"
#
#
# def update_convex_pools(pools: List[ConvexPool]):
#     container = get_container(CONTAINER_NAME)
#     for pool in pools:
#         container.upsert_item(ConvexPoolSchema().dump(pool))


def update_convex_pools(pools: List[ConvexPool]):
    try:
        for pool in pools:
            db.session.add(pool)
        db.session.commit()
    except Exception as e:
        print(f"Failed to add pools to database. Error: {e}")
        db.session.rollback()
