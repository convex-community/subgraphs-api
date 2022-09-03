from models.curve.pool import CurvePoolName, CurvePoolNameSchema, CurvePoolSchema, CurvePool, CurvePoolNameChainSchema, \
    CurvePoolNameChain
from services.query import query_db, get_container
from typing import List, Mapping
from marshmallow import EXCLUDE


def _exec_query(query: str) -> List:
    return query_db(get_container("CurvePools"), query)


def get_all_pool_names() -> List[CurvePoolNameChain]:
    query = f"SELECT c.address, c.chain, c.name FROM CurvePools as c"
    return CurvePoolNameChainSchema(many=True).load(_exec_query(query), unknown=EXCLUDE)


def get_pool_names(chain: str) -> List[CurvePoolName]:
    query = f"SELECT c.address, c.name FROM CurvePools as c WHERE c.chain = '{chain}'"
    return CurvePoolNameSchema(many=True).load(_exec_query(query), unknown=EXCLUDE)


def get_all_pool_metadata(chain: str) -> List[CurvePool]:
    query = f"SELECT * FROM CurvePools as c WHERE c.chain = '{chain}'"
    return CurvePoolSchema(many=True).load(_exec_query(query), unknown=EXCLUDE)


def get_pool_metadata(chain: str, pool: str) -> List[CurvePool]:
    query = f"SELECT * FROM CurvePools as c WHERE c.id = '{pool.lower()}-{chain}'"
    return CurvePoolSchema(many=True).load(_exec_query(query), unknown=EXCLUDE)
