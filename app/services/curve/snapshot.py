from models.curve.snapshot import (
    CurvePoolSnapshotSchema,
    CurvePoolSnapshot,
    CurvePoolVolumeSnapshot,
    CurvePoolVolumeSnapshotSchema,
    CurvePoolFeeSnapshotSchema,
    CurvePoolTVLSnapshotSchema,
    CurvePoolTVLSnapshot,
    CurvePoolFeeSnapshot,
    CurvePoolReserveSnapshot,
    CurvePoolReserveSchema,
)
from services.modules.utils import append_offset_and_limit
from services.query import query_db, get_container
from typing import List, Optional
from marshmallow import EXCLUDE
from main import db


def _exec_query(query: str) -> List:
    return query_db(get_container("CurvePoolSnapshots"), query)


def get_pool_snapshots(
    chain: str,
    pool: str,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
) -> List[CurvePoolSnapshot]:
    query = (
        db.session.query(CurvePoolSnapshot)
        .filter(
            CurvePoolSnapshot.pool == pool.lower(),
            CurvePoolSnapshot.chain == chain,
        )
        .order_by(CurvePoolSnapshot.timestamp.desc())
    )

    if offset is not None:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)

    result = query.all()
    result = [CurvePoolSnapshotSchema().load(row._asdict()) for row in result]
    return result


def get_pool_volume_snapshots(
    chain: str, pool: str
) -> List[CurvePoolVolumeSnapshot]:
    result = (
        db.session.query(CurvePoolSnapshot)
        .with_entities(
            CurvePoolSnapshot.volume,
            CurvePoolSnapshot.volumeUSD,
            CurvePoolSnapshot.timestamp,
        )
        .filter(
            CurvePoolSnapshot.pool == pool.lower(),
            CurvePoolSnapshot.chain == chain,
        )
        .order_by(CurvePoolSnapshot.timestamp.desc())
        .all()
    )
    result = [
        CurvePoolVolumeSnapshotSchema().load(row._asdict()) for row in result
    ]
    return result


def get_pool_fee_snapshots(
    chain: str, pool: str
) -> List[CurvePoolFeeSnapshot]:
    result = (
        db.session.query(CurvePoolSnapshot)
        .with_entities(
            CurvePoolSnapshot.totalDailyFeesUSD,
            CurvePoolSnapshot.adminFee,
            CurvePoolSnapshot.fee,
            CurvePoolSnapshot.timestamp,
        )
        .filter(
            CurvePoolSnapshot.pool == pool.lower(),
            CurvePoolSnapshot.chain == chain,
        )
        .order_by(CurvePoolSnapshot.timestamp.desc())
        .all()
    )
    result = [
        CurvePoolFeeSnapshotSchema().load(row._asdict()) for row in result
    ]
    return result


def get_pool_tvl_snapshots(
    chain: str, pool: str
) -> List[CurvePoolTVLSnapshot]:
    result = (
        db.session.query(CurvePoolSnapshot)
        .with_entities(CurvePoolSnapshot.tvl, CurvePoolSnapshot.timestamp)
        .filter(
            CurvePoolSnapshot.pool == pool.lower(),
            CurvePoolSnapshot.chain == chain,
        )
        .order_by(CurvePoolSnapshot.timestamp.desc())
        .all()
    )
    result = [
        CurvePoolTVLSnapshotSchema().load(row._asdict()) for row in result
    ]
    return result


def get_pool_reserves_snapshots(
    chain: str, pool: str
) -> List[CurvePoolReserveSnapshot]:
    result = (
        db.session.query(CurvePoolSnapshot)
        .with_entities(
            CurvePoolSnapshot.reserves,
            CurvePoolSnapshot.reservesUSD,
            CurvePoolSnapshot.timestamp,
        )
        .filter(
            CurvePoolSnapshot.pool == pool.lower(),
            CurvePoolSnapshot.chain == chain,
        )
        .order_by(CurvePoolSnapshot.timestamp.desc())
        .all()
    )
    result = [CurvePoolReserveSchema().load(row._asdict()) for row in result]
    return result
