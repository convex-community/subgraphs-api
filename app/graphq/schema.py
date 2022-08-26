import strawberry

from models.convex.pool import ConvexPool
from models.convex.snapshot import ConvexPoolSnapshot
from models.curve.pool import CurvePool
from models.curve.snapshot import CurvePoolSnapshot
from services import curve, convex


@strawberry.type
class Query:
    @strawberry.field
    def curve_pools(
        self,
        chain: str
    ) -> list[CurvePool]:
        return curve.get_all_pool_metadata(chain)

    @strawberry.field
    def curve_pool_snapshots(
        self,
        chain: str,
        pool: str
    ) -> list[CurvePoolSnapshot]:
        return curve.get_pool_snapshots(chain, pool)

    @strawberry.field
    def convex_pools(
        self,
    ) -> list[ConvexPool]:
        return convex.get_all_pool_metadata()

    @strawberry.field
    def convex_pool_snapshots(
        self,
        pool: str
    ) -> list[ConvexPoolSnapshot]:
        return convex.get_pool_snapshots(pool)


schema = strawberry.Schema(query=Query)

