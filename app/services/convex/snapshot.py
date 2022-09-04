from models.convex.snapshot import (
    ConvexPoolSnapshotSchema,
    ConvexPoolSnapshot,
    ConvexPoolAPRSnapshot,
    ConvexPoolAPRSnapshotSchema,
    ConvexPoolTVLSnapshotSchema,
    ConvexPoolTVLSnapshot,
)
from services.query import query_db, get_container
from typing import List
from marshmallow import EXCLUDE


def _exec_query(query: str) -> List:
    return query_db(get_container("ConvexPoolSnapshots"), query)


def get_pool_snapshots(pool: str) -> List[ConvexPoolSnapshot]:
    query = f"SELECT * FROM ConvexPoolSnapshots as c WHERE c.poolid = '{pool}' ORDER BY c.timestamp DESC"
    return ConvexPoolSnapshotSchema(many=True).load(
        _exec_query(query), unknown=EXCLUDE
    )


def get_pool_tvl_snapshots(pool: str) -> List[ConvexPoolTVLSnapshot]:
    query = f"SELECT c.tvl, c.curveTvlRatio, c.timestamp FROM ConvexPoolSnapshots as c WHERE c.poolid = '{pool}' ORDER BY c.timestamp DESC"
    return ConvexPoolTVLSnapshotSchema(many=True).load(
        _exec_query(query), unknown=EXCLUDE
    )


def get_pool_apr_snapshots(pool: str) -> List[ConvexPoolAPRSnapshot]:
    query = f"SELECT c.baseApr, c.crvApr, c.cvxApr, c.extraRewardsApr, c.timestamp FROM ConvexPoolSnapshots as c WHERE c.poolid = '{pool}' ORDER BY c.timestamp DESC"
    return ConvexPoolAPRSnapshotSchema(many=True).load(
        _exec_query(query), unknown=EXCLUDE
    )
