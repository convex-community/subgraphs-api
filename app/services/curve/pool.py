from models.curve.pool import (
    CurvePoolName,
    CurvePoolNameSchema,
    CurvePoolSchema,
    CurvePool,
    CurvePoolNameChainSchema,
    CurvePoolNameChain,
)
from main import db
from typing import List, Mapping
from marshmallow import EXCLUDE


def get_all_pool_names() -> List[CurvePoolNameChain]:
    result = db.query(CurvePool.address, CurvePool.chain, CurvePool.name).all()
    return CurvePoolNameChainSchema(many=True, session=db.session).load(
        result, unknown=EXCLUDE
    )


def get_pool_names(chain: str) -> List[CurvePoolName]:
    result = (
        db.query(CurvePool.address, CurvePool.name)
        .filter(CurvePool.chain == chain)
        .all()
    )
    return CurvePoolNameSchema(many=True, session=db.session).load(
        result, unknown=EXCLUDE
    )


def get_all_pool_metadata(chain: str) -> List[CurvePool]:
    result = db.query(CurvePool).filter(CurvePool.chain == chain).all()
    return CurvePoolSchema(many=True, session=db.session).load(
        result, unknown=EXCLUDE
    )


def get_pool_metadata(chain: str, pool: str) -> List[CurvePool]:
    result = (
        db.query(CurvePool)
        .filter(CurvePool.id == f"{pool.lower()}-{chain}")
        .all()
    )
    return CurvePoolSchema(many=True, session=db.session).load(
        result, unknown=EXCLUDE
    )
