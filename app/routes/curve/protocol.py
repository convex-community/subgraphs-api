from flask_restx import Resource, Namespace, fields, reqparse
import json
from main.const import CHAINS
from models.curve.rankings import (
    TopTvlChange,
    TopLiquidityUse,
    PoolTypeVolume,
    PoolTypeTvl,
    ChainTvl,
    ChainVolume,
    LargeTrades,
)
from models.curve.revenue import (
    CurveChainRevenue,
    CurveHistoricalPoolCumulativeRevenue,
    CurveChainTopPoolRevenue,
    CurvePoolRevenue,
    CouchCushion,
    WeeklyFeesSnapshot,
)
from routes import cache
from services.curve.revenue import (
    get_platform_revenue,
    get_top_pools,
    get_top_chain_pools,
    get_pool_revenue,
    check_couch_cushion,
    get_historical_fee_breakdown,
)
from utils import convert_schema
from main import redis

api = Namespace("protocol", description="Protocol endpoints")
pool_rev = api.model("Pool Revenue", convert_schema(CurvePoolRevenue))
chain_rev = api.model("Chain Revenue", convert_schema(CurveChainRevenue))
top_pools = api.model(
    "Top Pools", convert_schema(CurveHistoricalPoolCumulativeRevenue)
)
chain_top_pools = api.model(
    "Chain Top Pools", convert_schema(CurveChainTopPoolRevenue)
)
chains = api.model("Supported Chains", {"chains": fields.List(fields.String)})
top_tvl = api.model("Top TVL Change", convert_schema(TopTvlChange))
top_liq = api.model(
    "Top Liquidity Utilisation", convert_schema(TopLiquidityUse)
)
type_vol = api.model(
    "Volume Distribution by Pool Type", convert_schema(PoolTypeVolume)
)
type_tvl = api.model(
    "TVL Distribution by Pool Type", convert_schema(PoolTypeTvl)
)
chain_tvl = api.model("TVL Distribution by Chain", convert_schema(ChainTvl))
chain_vol = api.model(
    "Volume Distribution by Chain", convert_schema(ChainVolume)
)
large_trades = api.model("Largest trades", convert_schema(LargeTrades))
couch = api.model("Check couch cushions", convert_schema(CouchCushion))
weekly_breakdown = api.model(
    "Weekly revenue breakdown", convert_schema(WeeklyFeesSnapshot)
)


breakdown = reqparse.RequestParser()
breakdown.add_argument(
    "from",
    type=int,
    help="Date (unix timestamp) to start from",
    required=False,
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


@api.route("/chains")
@api.doc(description="Get the supported chains")
@api.response(404, "Chain or pool not found")
class ChainList(Resource):
    @api.marshal_with(chains)
    def get(self):
        return {"chains": CHAINS}


@api.route("/<string:chain>/factories")
@api.doc(description="Get all historical factory contracts")
@api.param("chain", "Chain to query for")
@api.response(404, "Chain or pool not found")
class FactoryList(Resource):
    def get(self, chain, pool):
        print(chain)
        return pool


@api.route("/<string:chain>/registries")
@api.doc(description="Get all historical registry contracts")
@api.param("chain", "Chain to query for")
@api.response(404, "Chain or pool not found")
class RegistryList(Resource):
    def get(self, chain, pool):
        print(chain)
        return pool


@api.route("/revenue/historical/breakdown")
@api.doc(description="Get weekly revenue breakdown by chain & crvusd")
@api.response(404, "Not found")
@api.expect(breakdown)
class WeeklyRevenueBreakdown(Resource):
    # @cache.cached(timeout=60)
    @api.marshal_list_with(weekly_breakdown, envelope="revenue")
    def get(self):
        args = breakdown.parse_args()
        start = args.get("from", 0)
        return get_historical_fee_breakdown(start)


@api.route("/revenue/historical/toppools/<int:top>")
@api.doc(description="Get weekly revenue of top pools vs others")
@api.param("top", "Number of top pools to single out")
@api.response(404, "Not found")
class TopPoolList(Resource):
    @cache.cached(timeout=60 * 15)
    @api.marshal_list_with(top_pools, envelope="revenue")
    def get(self, top):
        return get_top_pools(top)


@api.route("/revenue/<string:chain>/toppools/<int:top>")
@api.doc(description="Get top pools by revenue for a chain for previous week")
@api.param("chain", "Name of the chain to query for")
@api.response(404, "Not found")
class ChainTopPoolList(Resource):
    @cache.cached(timeout=60 * 15)
    @check_exists
    @api.marshal_list_with(chain_top_pools, envelope="revenue")
    def get(self, chain, top):
        return get_top_chain_pools(chain.lower(), top)


@api.route(
    '/revenue/<regex("[A-z0-9]+"):chain>/historical/<regex("[A-z0-9]+"):pool>'
)
@api.doc(description="Get the historical revenue for a pool")
@api.param("chain", "Name of the chain to query for")
@api.param("pool", "Name of the pool to query for")
@api.response(404, "Not found")
class ChainPoolRevenue(Resource):
    @cache.cached(timeout=60 * 15)
    @check_exists
    @api.marshal_list_with(pool_rev, envelope="revenue")
    def get(self, chain, pool):
        return get_pool_revenue(chain.lower(), pool.lower())


@api.route("/revenue/chains")
@api.doc(description="Get total revenue accumulated on each chain")
@api.response(404, "Chain or pool not found")
class RevenueByChain(Resource):
    @cache.cached(timeout=60 * 15)
    @api.marshal_list_with(chain_rev, envelope="revenue")
    def get(self):
        return get_platform_revenue()


@api.route("/tvl/gainers")
@api.doc(description="Get pools with the most TVL increase over past 24h")
@api.response(404, "Chain or pool not found")
class TVLGainers(Resource):
    @api.marshal_list_with(top_tvl, envelope="tvl_gainers")
    def get(self):
        return json.loads(redis.get("tvl_gainers"))


@api.route("/tvl/losers")
@api.doc(description="Get pools with the least TVL increase over past 24h")
class TVLLosers(Resource):
    @api.marshal_list_with(top_tvl, envelope="tvl_losers")
    def get(self):
        return json.loads(redis.get("tvl_losers"))


@api.route("/tvl/chain_breakdown")
@api.doc(description="Get TVL Distribution by Chain over past 24h")
class ChainTvlBreakdown(Resource):
    @api.marshal_list_with(chain_tvl, envelope="tvl_breakdown_chain")
    def get(self):
        return json.loads(redis.get("tvl_breakdown_chain"))


@api.route("/volume/chain_breakdown")
@api.doc(description="Get Volume Distribution by Chain over past 24h")
class ChainVolBreakdown(Resource):
    @api.marshal_list_with(chain_vol, envelope="volume_breakdown_chain")
    def get(self):
        return json.loads(redis.get("volume_breakdown_chain"))


@api.route("/tvl/type_breakdown")
@api.doc(description="Get TVL Distribution by pool type over past 24h")
class TypeTvl(Resource):
    @api.marshal_list_with(type_tvl, envelope="tvl_breakdown_type")
    def get(self):
        return json.loads(redis.get("tvl_breakdown_type"))


@api.route("/volume/type_breakdown")
@api.doc(description="Get Volume Distribution by pool type over past 24h")
class TypeVol(Resource):
    @api.marshal_list_with(type_vol, envelope="volume_breakdown_type")
    def get(self):
        return json.loads(redis.get("volume_breakdown_type"))


@api.route("/liquidity/top")
@api.doc(description="Get top pools by liquidity utilisation over past 24h")
class LiquidityUtilisationTop(Resource):
    @api.marshal_list_with(top_liq, envelope="liquidity_use")
    def get(self):
        return json.loads(redis.get("big_users"))


@api.route("/size/trades")
@api.doc(description="Get most sizeable trades over past 24h")
class SizeableTrades(Resource):
    @api.marshal_list_with(large_trades, envelope="large_trades")
    def get(self):
        return json.loads(redis.get("sizeable_trades"))


@api.route("/couch/cushions")
@api.doc(description="Check under the cushions on all chain's couches")
class CheckCushions(Resource):
    @api.marshal_list_with(couch, envelope="cushions")
    def get(self):
        cushions = check_couch_cushion()
        return cushions
