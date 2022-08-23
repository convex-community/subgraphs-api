from tasks.database.client import get_container
from typing import List
from models.curve.pool import CurvePool, CurvePoolSchema

CONTAINER_NAME = "CurvePools"


def update_curve_pools(pools: List[CurvePool]):
    container = get_container(CONTAINER_NAME)
    for pool in pools:
        container.upsert_item(CurvePoolSchema().dump(pool))