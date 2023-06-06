from operator import and_

from sqlalchemy import func

from main import db
from models.curve.crvusd import CrvUsdPoolStatSchema, CrvUsdPoolStat
from models.curve.pool import CurvePoolName, CurvePool, CurvePoolNameSchema
from main.const import PoolType
from models.curve.snapshot import CurvePoolSnapshot


def get_crv_usd_pool_names() -> list[CurvePoolName]:
    result = (
        db.session.query(CurvePool)
        .with_entities(CurvePool.address, CurvePool.name)
        .filter(CurvePool.poolType == PoolType.CRVUSD.value)
        .all()
    )

    result = [CurvePoolNameSchema().load(row._asdict()) for row in result]

    return result


def get_crv_usd_pool_stats() -> list[CrvUsdPoolStat]:
    subquery = (
        db.session.query(
            CurvePoolSnapshot.pool,
            func.max(CurvePoolSnapshot.timestamp).label("max_timestamp"),
        )
        .group_by(CurvePoolSnapshot.pool)
        .subquery()
    )
    import logging

    logger = logging.getLogger(__name__)
    logger.error(
        db.session.query(
            CurvePoolSnapshot.pool,
            func.max(CurvePoolSnapshot.timestamp).label("max_timestamp"),
        )
        .group_by(CurvePoolSnapshot.pool)
        .all()
    )

    query = (
        db.session.query(
            CurvePool.address,
            CurvePool.name,
            CurvePoolSnapshot.tvl,
            CurvePoolSnapshot.normalizedReserves,
            CurvePoolSnapshot.reservesUSD,
            CurvePoolSnapshot.volumeUSD,
        )
        .join(CurvePoolSnapshot, CurvePool.address == CurvePoolSnapshot.pool)
        .join(
            subquery,
            and_(
                CurvePoolSnapshot.pool == subquery.c.pool,
                CurvePoolSnapshot.timestamp == subquery.c.max_timestamp,
            ),
        )
        .filter(CurvePool.poolType == PoolType.CRVUSD.value)
    )
    res = query.all()
    logger.warning(res)
    results = []
    for row in query.all():
        result = CrvUsdPoolStatSchema().load(row._asdict())
        result.name = result.name.split("Pool: ")[-1]
        results.append(result)

    return results
