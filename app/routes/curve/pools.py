import time
from flask_restx import Resource, Namespace, reqparse

from models.curve.bonding import CurvePoolBondingCurve
from models.curve.returns import CurveReturnSeries
from routes import cache
from main.const import CHAINS
from models.curve.snapshot import (
    CurvePoolSnapshot,
    CurvePoolVolumeSnapshot,
    CurvePoolFeeSnapshot,
    CurvePoolTVLSnapshot,
    CurvePoolReserveSnapshot,
)
from services.curve.bonding import (
    get_v1_curve,
    get_v2_curve,
    get_bonding_curves,
)
from services.curve.returns import get_returns
from services.curve.snapshot import (
    get_pool_snapshots,
    get_pool_volume_snapshots,
    get_pool_fee_snapshots,
    get_pool_reserves_snapshots,
    get_pool_tvl_snapshots,
)
from utils import convert_schema
from models.curve.pool import CurvePoolName, CurvePool
from services.curve.pool import (
    get_pool_names,
    get_all_pool_metadata,
    get_pool_metadata,
)

api = Namespace("pools", description="Pools endpoints")
names = api.model("Pool Name", convert_schema(CurvePoolName))
metadata = api.model("Pool Metadata", convert_schema(CurvePool))
snapshots = api.model("Pool Snapshot", convert_schema(CurvePoolSnapshot))
volume = api.model("Pool Volume", convert_schema(CurvePoolVolumeSnapshot))
fees = api.model("Pool Fees", convert_schema(CurvePoolFeeSnapshot))
tvl = api.model("Pool TVL", convert_schema(CurvePoolTVLSnapshot))
bonding = api.model(
    "Pool Bonding Curves", convert_schema(CurvePoolBondingCurve)
)
reserves = api.model("Pool Reserves", convert_schema(CurvePoolReserveSnapshot))
returns = api.model("Pool Returns", convert_schema(CurveReturnSeries))

v1_parser = reqparse.RequestParser()
v1_parser.add_argument(
    "A",
    type=int,
    help="Amplification parameter",
    required=True,
    location="form",
)
v1_parser.add_argument(
    "xp",
    type=str,
    help="List of reserves (normalized to 18 decimals)",
    action="split",
    required=True,
    location="form",
)
v1_parser.add_argument(
    "coins",
    type=str,
    help="List of asset names",
    action="split",
    required=True,
    location="form",
)
v1_parser.add_argument(
    "resolution",
    type=int,
    help="Number of data points",
    default=1000,
    location="form",
)

v2_parser = reqparse.RequestParser()
v2_parser.add_argument(
    "A",
    type=int,
    help="Amplification parameter",
    required=True,
    location="form",
)
v2_parser.add_argument(
    "gamma",
    type=int,
    help="Amplification parameter",
    required=True,
    location="form",
)
v2_parser.add_argument(
    "xp",
    type=str,
    help="List of reserves (normalized to invariant)",
    action="split",
    required=True,
    location="form",
)
v2_parser.add_argument(
    "coins",
    type=str,
    help="List of asset names",
    action="split",
    required=True,
    location="form",
)
v2_parser.add_argument(
    "resolution",
    type=int,
    help="Number of data points",
    default=1000,
    location="form",
)


il_parser = reqparse.RequestParser()
il_parser.add_argument(
    "start_date",
    type=int,
    help="Starting date",
    default=1577836800,
    location="args",
)
il_parser.add_argument(
    "end_date",
    type=int,
    help="End date",
    default=int(time.time()),
    location="args",
)
il_parser.add_argument(
    "lp_tokens",
    type=str,
    help="Number of LP Tokens (18 decimals)",
    default="1000000000000000000",
    location="args",
)


def check_exists(func):
    def wrapped(*args, **kwargs):
        if kwargs["chain"] not in CHAINS:
            api.abort(404)
        data = func(*args, **kwargs)
        if not data:
            api.abort(404)
        return data

    return wrapped


@api.route("/<string:chain>/")
@api.doc(description="Get all pool names & addresses")
@api.response(404, "Chain or pool not found")
class PoolList(Resource):
    @api.marshal_list_with(names, envelope="pools")
    @cache.cached(timeout=60 * 15)
    @check_exists
    def get(self, chain):
        return get_pool_names(chain)


@api.route("/<string:chain>/all")
@api.doc(description="Get all pools' metadata")
@api.response(404, "Chain or pool not found")
class PoolMetadata(Resource):
    @api.marshal_list_with(metadata, envelope="pools")
    @cache.cached(timeout=60 * 15)
    @check_exists
    def get(self, chain):
        return get_all_pool_metadata(chain)


@api.route('/<string:chain>/<regex("[A-z0-9]+"):pool>')
@api.doc(description="Get pool metadata")
@api.param("chain", "Chain to query for")
@api.param("pool", "Pool to query volume for")
@api.response(404, "Chain or pool not found")
class Pool(Resource):
    @api.marshal_with(metadata, envelope="pools")
    @cache.cached(timeout=60 * 15)
    @check_exists
    def get(self, chain, pool):
        return get_pool_metadata(chain.lower(), pool.lower())


@api.route('/<string:chain>/snapshots/<regex("[A-z0-9]+"):pool>')
@api.doc(description="Get historical pool snapshots")
@api.param("chain", "Chain to query for")
@api.param("pool", "Pool to query volume for")
@api.response(404, "Chain or pool not found")
class PoolSnapshots(Resource):
    @api.marshal_list_with(snapshots, envelope="snapshots")
    @cache.cached()
    @check_exists
    def get(self, chain, pool):
        return get_pool_snapshots(chain.lower(), pool.lower())


@api.route('/<string:chain>/swaps/<regex("[A-z0-9]+"):pool>')
@api.doc(description="Get pool swap events")
@api.param("chain", "Chain to query for")
@api.param("pool", "Pool to query volume for")
@api.response(404, "Chain or pool not found")
class PoolSwaps(Resource):
    @cache.cached(timeout=60 * 15)
    def get(self, chain, pool):
        print(chain)
        return pool


@api.route('/<string:chain>/candles/<regex("[A-z0-9]+"):pool>')
@api.doc(description="Get pool price candles")
@api.param("chain", "Chain to query for")
@api.param("pool", "Pool to query volume for")
@api.response(404, "Chain or pool not found")
class PoolCandles(Resource):
    @cache.cached(timeout=60 * 15)
    def get(self, chain, pool):
        print(chain)
        return pool


@api.route('/<string:chain>/volume/<regex("[A-z0-9]+"):pool>')
@api.doc(description="Get historical pool volume")
@api.param("chain", "Chain to query for")
@api.param("pool", "Pool to query volume for")
@api.response(404, "Chain or pool not found")
class PoolVolume(Resource):
    @api.marshal_list_with(volume, envelope="volume")
    @cache.cached()
    @check_exists
    def get(self, chain, pool):
        return get_pool_volume_snapshots(chain.lower(), pool.lower())


@api.route('/<string:chain>/fees/<regex("[A-z0-9]+"):pool>')
@api.doc(description="Get historical pool fees")
@api.param("chain", "Chain to query for")
@api.param("pool", "Pool to query fees for")
@api.response(404, "Chain or pool not found")
class PoolFees(Resource):
    @api.marshal_list_with(fees, envelope="fees")
    @cache.cached()
    @check_exists
    def get(self, chain, pool):
        return get_pool_fee_snapshots(chain.lower(), pool.lower())


@api.route('/<string:chain>/reserves/<regex("[A-z0-9]+"):pool>')
@api.doc(description="Get historical pool reserves")
@api.param("chain", "Chain to query for")
@api.param("pool", "Pool to query reserves for")
@api.response(404, "Chain or pool not found")
class PoolReserves(Resource):
    @api.marshal_list_with(reserves, envelope="reserves")
    @cache.cached()
    @check_exists
    def get(self, chain, pool):
        return get_pool_reserves_snapshots(chain.lower(), pool.lower())


@api.route('/<string:chain>/tvl/<regex("[A-z0-9]+"):pool>')
@api.doc(description="Get historical pool TVL")
@api.param("chain", "Chain to query for")
@api.param("pool", "Pool to query TVL for")
@api.response(404, "Chain or pool not found")
class PoolValue(Resource):
    @api.marshal_list_with(tvl, envelope="tvl")
    @cache.cached()
    @check_exists
    def get(self, chain, pool):
        return get_pool_tvl_snapshots(chain.lower(), pool.lower())


@api.route('/<string:chain>/emissions/<regex("[A-z0-9]+"):pool>')
@api.doc(description="Get pool emissions")
@api.param("chain", "Chain to query for")
@api.param("pool", "Pool to query volume for")
@api.response(404, "Chain or pool not found")
class PoolEmissions(Resource):
    def get(self, chain, pool):
        print(chain)
        return pool


@api.route("/curve/v1")
@api.doc(description="Get the bonding curve of a v1 pool based on its params")
@api.expect(v1_parser)
class V1BondingCurve(Resource):
    @api.marshal_list_with(bonding, envelope="curves")
    def post(self):
        args = v1_parser.parse_args()
        return get_v1_curve(**args)


@api.route("/curve/v2")
@api.doc(description="Get the bonding curve of a v2 pool based on its params")
@api.expect(v2_parser)
class V2BondingCurve(Resource):
    @api.marshal_list_with(bonding, envelope="curves")
    def post(self):
        args = v2_parser.parse_args()
        return get_v2_curve(**args)


@api.route('/<string:chain>/curve/<regex("[A-z0-9]+"):pool>')
@api.doc(description="Get the bonding curve of a specific pool")
@api.param("chain", "Chain to query for")
@api.param("pool", "Pool to query volume for")
@api.response(404, "Chain or pool not found")
class PoolBondingCurve(Resource):
    @api.marshal_list_with(bonding, envelope="curves")
    @cache.cached(timeout=60)
    @check_exists
    def get(self, chain, pool):
        return get_bonding_curves(chain, pool, 1000)


@api.route('/<string:chain>/returns/<regex("[A-z0-9]+"):pool>')
@api.doc(description="Get IL/yield info for a specific pool")
@api.param("chain", "Chain to query for")
@api.param("pool", "Pool to query volume for")
@api.expect(il_parser)
@api.response(404, "Chain or pool not found")
class PoolReturnsInfo(Resource):
    @api.marshal_list_with(returns, envelope="returns")
    @cache.cached(timeout=1)
    @check_exists
    def get(self, chain, pool):
        args = il_parser.parse_args()
        data = get_returns(chain, pool.lower(), **args)
        if data:
            return data
        api.abort(404)
