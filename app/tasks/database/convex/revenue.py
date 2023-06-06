from models.convex.revenue import (
    ConvexRevenueSnapshot,
    ConvexCumulativeRevenue,
)
from typing import List
from main import db


def update_convex_revenue_snapshots(pools: List[ConvexRevenueSnapshot]):
    for pool in pools:
        db.session.merge(pool)
    db.session.commit()


def update_convex_cumulative_revenue(data: ConvexCumulativeRevenue):
    if data:
        db.session.merge(data)
        db.session.commit()
