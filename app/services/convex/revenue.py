from models.convex.revenue import (
    ConvexCumulativeRevenue,
    ConvexRevenueSnapshot,
    ConvexRevenueSnapshotSchema,
    ConvexRevenueSnapshotData,
    ConvexRevenueSnapshotDataSchema,
)
from sqlalchemy import asc
from typing import List
from main import db
from marshmallow import EXCLUDE
import pandas as pd

GROUPER_MAPPING = {"w": "W-TUE", "m": "M", "y": "A"}


def get_platform_total_revenue() -> List[ConvexCumulativeRevenue]:
    return db.session.query(ConvexCumulativeRevenue).all()


def get_platform_revenue_snapshots(
    groupby: str = "w",
) -> List[ConvexRevenueSnapshotData]:
    res = (
        db.session.query(ConvexRevenueSnapshot)
        .order_by(asc(ConvexRevenueSnapshot.timestamp))
        .all()
    )
    res = [ConvexRevenueSnapshotSchema().dump(r) for r in res]
    if groupby != "d":
        df = pd.DataFrame(res)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df = df.groupby(
            pd.Grouper(key="timestamp", freq=GROUPER_MAPPING.get(groupby, "w"))
        ).sum(numeric_only=True)
        df.reset_index(inplace=True)
        df["timestamp"] = df["timestamp"].astype(int) // int(1e9)
        df["id"] = df["timestamp"].astype(str)
        res = df.to_dict(orient="records")

    return ConvexRevenueSnapshotDataSchema.load(
        res, unknown=EXCLUDE, many=True
    )
