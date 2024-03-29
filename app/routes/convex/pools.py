from flask_restx import Resource, Namespace
from routes import cache
from models.convex.snapshot import (
    ConvexPoolSnapshot,
    ConvexPoolTVLSnapshot,
    ConvexPoolAPRSnapshot,
)
from services.convex.snapshot import (
    get_pool_snapshots,
    get_pool_tvl_snapshots,
    get_pool_apr_snapshots,
)
from services.convex.pool import get_pool_names
from utils import convert_schema
from models.convex.pool import ConvexPool, ConvexPoolName
from services.convex.pool import get_all_pool_metadata, get_pool_metadata

api = Namespace("pools", description="Pools endpoints")
names = api.model("Pool Name", convert_schema(ConvexPoolName))
metadata = api.model("Pool Metadata", convert_schema(ConvexPool))
snapshot = api.model("Pool Snapshot", convert_schema(ConvexPoolSnapshot))
tvl = api.model("Pool TVL", convert_schema(ConvexPoolTVLSnapshot))
apr = api.model("Pool APR", convert_schema(ConvexPoolAPRSnapshot))


def check_exists(func):
    def wrapped(*args, **kwargs):
        data = func(*args, **kwargs)
        if not data:
            api.abort(404)
        return data

    return wrapped


@api.route("/")
@api.doc(description="Get all pool names & ids")
@api.response(404, "Pool not found")
class PoolList(Resource):
    @api.marshal_list_with(names, envelope="pools")
    @cache.cached(timeout=60)
    @check_exists
    def get(self):
        return get_pool_names()


@api.route("/all")
@api.doc(description="Get all pools' metadata")
@api.response(404, "Pool not found")
class PoolMetadata(Resource):
    @api.marshal_list_with(metadata, envelope="pools")
    @cache.cached(timeout=60)
    @check_exists
    def get(self):
        return get_all_pool_metadata()


@api.route("/<int:poolid>")
@api.doc(description="Get pool metadata")
@api.param("poolid", "ID of pool to query")
@api.response(404, "Pool not found")
class Pool(Resource):
    @api.marshal_with(metadata, envelope="pools")
    @cache.cached(timeout=60)
    @check_exists
    def get(self, poolid):
        return get_pool_metadata(poolid)


@api.route("/snapshots/<int:poolid>")
@api.doc(description="Get historical pool snapshots")
@api.param("poolid", "ID of pool to get historical data for")
@api.response(404, "Pool not found")
class PoolSnapshots(Resource):
    @api.marshal_list_with(snapshot, envelope="snapshots")
    @cache.cached()
    @check_exists
    def get(self, poolid):
        return get_pool_snapshots(poolid)


@api.route("/apr/<int:poolid>")
@api.doc(description="Get historical pool APR")
@api.param("poolid", "ID of pool to query APR for")
@api.response(404, "Pool not found")
class PoolAPRSnapshots(Resource):
    @api.marshal_list_with(apr, envelope="apr")
    @cache.cached()
    @check_exists
    def get(self, poolid):
        return get_pool_apr_snapshots(poolid)


@api.route("/tvl/<int:poolid>")
@api.doc(description="Get historical pool TVL")
@api.param("poolid", "ID of pool to query TVL for")
@api.response(404, "Pool not found")
class PoolTVLSnapshots(Resource):
    @api.marshal_list_with(tvl, envelope="tvl")
    @cache.cached()
    @check_exists
    def get(self, poolid):
        return get_pool_tvl_snapshots(poolid)
