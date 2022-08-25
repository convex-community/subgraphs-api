from models.convex.pool import ConvexPool, ConvexPoolSchema
from tasks.database.client import get_container
from typing import List

CONTAINER_NAME = "ConvexPools"


def update_convex_pools(pools: List[ConvexPool]):
    container = get_container(CONTAINER_NAME)
    for pool in pools:
        container.upsert_item(ConvexPoolSchema().dump(pool))
