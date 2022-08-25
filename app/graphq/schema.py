import strawberry
from models.curve.pool import CurvePool
from models.curve.snapshot import CurvePoolSnapshot
from services.curve.pool import get_all_pool_metadata
from services.curve.snapshot import get_pool_snapshots


@strawberry.type
class Query:
    @strawberry.field
    def curve_pools(
        self,
        chain: str
    ) -> list[CurvePool]:
        return get_all_pool_metadata(chain)

    @strawberry.field
    def curve_pool_snapshots(
        self,
        chain: str,
        pool: str
    ) -> list[CurvePoolSnapshot]:
        return get_pool_snapshots(chain, pool)


schema = strawberry.Schema(query=Query)

