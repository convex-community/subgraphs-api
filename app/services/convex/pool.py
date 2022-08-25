from models.convex.pool import ConvexPool, ConvexPoolSchema
from services.query import query_db, get_container
from typing import List
from marshmallow import EXCLUDE


def _exec_query(query: str) -> List:
    return query_db(get_container("ConvexPools"), query)


def get_all_pool_metadata() -> List[ConvexPool]:
    query = f"SELECT * FROM ConvexPools"
    return ConvexPoolSchema(many=True).load(_exec_query(query), unknown=EXCLUDE)
