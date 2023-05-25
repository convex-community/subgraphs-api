from models.convex.snapshot import (
    ConvexPoolSnapshot,
    ConvexPoolAPRSnapshot,
    ConvexPoolAPRSnapshotSchema,
    ConvexPoolTVLSnapshotSchema,
    ConvexPoolTVLSnapshot,
)
from typing import List
from sqlalchemy import desc
from main import db


def get_pool_snapshots(pool: int) -> List[ConvexPoolSnapshot]:
    return (
        db.session.query(ConvexPoolSnapshot)
        .filter(ConvexPoolSnapshot.poolid == str(pool))
        .order_by(desc(ConvexPoolSnapshot.timestamp))
        .all()
    )


def get_pool_tvl_snapshots(pool: int) -> List[ConvexPoolTVLSnapshot]:
    result = (
        db.session.query(
            ConvexPoolSnapshot.tvl,
            ConvexPoolSnapshot.curveTvlRatio,
            ConvexPoolSnapshot.timestamp,
        )
        .filter(ConvexPoolSnapshot.poolid == str(pool))
        .order_by(desc(ConvexPoolSnapshot.timestamp))
        .all()
    )
    return [
        ConvexPoolTVLSnapshotSchema().load(
            {"tvl": r[0], "curveTvlRatio": r[1], "timestamp": r[2]}
        )
        for r in result
    ]


def get_pool_apr_snapshots(pool: int) -> List[ConvexPoolAPRSnapshot]:
    result = (
        db.session.query(
            ConvexPoolSnapshot.baseApr,
            ConvexPoolSnapshot.crvApr,
            ConvexPoolSnapshot.cvxApr,
            ConvexPoolSnapshot.extraRewardsApr,
            ConvexPoolSnapshot.timestamp,
        )
        .filter(ConvexPoolSnapshot.poolid == str(pool))
        .order_by(desc(ConvexPoolSnapshot.timestamp))
        .all()
    )
    return [
        ConvexPoolAPRSnapshotSchema().load(
            {
                "baseApr": r[0],
                "crvApr": r[1],
                "cvxApr": r[2],
                "extraRewardsApr": r[3],
                "timestamp": r[4],
            }
        )
        for r in result
    ]
