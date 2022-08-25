from models.curve.snapshot import CurvePoolSnapshotSchema, CurvePoolSnapshot, CurvePoolVolumeSnapshot, \
    CurvePoolVolumeSnapshotSchema, CurvePoolFeeSnapshotSchema, CurvePoolTVLSnapshotSchema, CurvePoolTVLSnapshot, \
    CurvePoolFeeSnapshot, CurvePoolReserveSnapshot, CurvePoolReserveSchema
from services.query import query_db, get_container
from typing import List, Mapping
from marshmallow import EXCLUDE


def _exec_query(query: str) -> List:
    return query_db(get_container("CurvePoolSnapshots"), query)


def get_pool_snapshots(chain: str, pool: str) -> List[CurvePoolSnapshot]:
    query = f"SELECT * FROM CurvePoolSnapshots as c WHERE c.pool = '{pool.lower()}' AND c.chain = '{chain}' ORDER BY c.timestamp DESC"
    return CurvePoolSnapshotSchema(many=True).load(_exec_query(query), unknown=EXCLUDE)


def get_pool_volume_snapshots(chain: str, pool: str) -> List[CurvePoolVolumeSnapshot]:
    query = f"SELECT c.volume, c.volumeUSD, c.timestamp FROM CurvePoolSnapshots as c WHERE c.pool = '{pool.lower()}' AND c.chain = '{chain}' ORDER BY c.timestamp DESC"
    return CurvePoolVolumeSnapshotSchema(many=True).load(_exec_query(query), unknown=EXCLUDE)


def get_pool_fee_snapshots(chain: str, pool: str) -> List[CurvePoolFeeSnapshot]:
    query = f"SELECT c.totalDailyFeesUSD, c.adminFee, c.fee, c.timestamp FROM CurvePoolSnapshots as c WHERE c.pool = '{pool.lower()}' AND c.chain = '{chain}' ORDER BY c.timestamp DESC"
    return CurvePoolFeeSnapshotSchema(many=True).load(_exec_query(query), unknown=EXCLUDE)


def get_pool_tvl_snapshots(chain: str, pool: str) -> List[CurvePoolTVLSnapshot]:
    query = f"SELECT c.tvl, c.timestamp FROM CurvePoolSnapshots as c WHERE c.pool = '{pool.lower()}' AND c.chain = '{chain}' ORDER BY c.timestamp DESC"
    return CurvePoolTVLSnapshotSchema(many=True).load(_exec_query(query), unknown=EXCLUDE)


def get_pool_reserves_snapshots(chain: str, pool: str) -> List[CurvePoolReserveSnapshot]:
    query = f"SELECT c.reserves, c.reservesUSD, c.timestamp FROM CurvePoolSnapshots as c WHERE c.pool = '{pool.lower()}' AND c.chain = '{chain}' ORDER BY c.timestamp DESC"
    return CurvePoolReserveSchema(many=True).load(_exec_query(query), unknown=EXCLUDE)
