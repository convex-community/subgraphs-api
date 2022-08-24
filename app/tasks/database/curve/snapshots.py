from tasks.database.client import get_container
from typing import List
from models.curve.snapshot import CurvePoolSnapshot, CurvePoolSnapshotSchema

CONTAINER_NAME = "CurvePoolSnapshots"


def update_curve_pool_snapshots(snapshots: List[CurvePoolSnapshot]):
    container = get_container(CONTAINER_NAME)
    for snapshot in snapshots:
        container.upsert_item(CurvePoolSnapshotSchema().dump(snapshot))
