from flask_restx import Resource, Namespace, fields

from main.const import CHAINS
from models.curve.revenue import (
    CurveChainRevenue,
    CurveHistoricalPoolCumulativeRevenue,
    CurveChainTopPoolRevenue,
    CurvePoolRevenue,
)
from routes import cache
from services.curve.revenue import (
    get_platform_revenue,
    get_top_pools,
    get_top_chain_pools,
    get_pool_revenue,
)
from utils import convert_marshmallow

api = Namespace("protocol", description="Protocol endpoints")
pool_rev = api.model("Pool Revenue", convert_marshmallow(CurvePoolRevenue))
chain_rev = api.model("Chain Revenue", convert_marshmallow(CurveChainRevenue))
top_pools = api.model(
    "Top Pools", convert_marshmallow(CurveHistoricalPoolCumulativeRevenue)
)
chain_top_pools = api.model(
    "Chain Top Pools", convert_marshmallow(CurveChainTopPoolRevenue)
)
chains = api.model("Supported Chains", {"chains": fields.List(fields.String)})


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


@api.route("/revenue/historical/toppools/<int:top>")
@api.doc(description="Get weekly revenue of top pools vs others")
@api.param("top", "Number of top pools to single out")
@api.response(404, "Not found")
class TopPoolList(Resource):
    @api.marshal_list_with(top_pools, envelope="revenue")
    def get(self, top):
        return get_top_pools(top)


@api.route("/revenue/<string:chain>/toppools/<int:top>")
@api.doc(description="Get top pools by revenue for a chain for previous week")
@api.param("chain", "Name of the chain to query for")
@api.response(404, "Not found")
class ChainTopPoolList(Resource):
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
    @cache.cached()
    @check_exists
    @api.marshal_list_with(pool_rev, envelope="revenue")
    def get(self, chain, pool):
        return get_pool_revenue(chain.lower(), pool.lower())


@api.route("/revenue/chains")
@api.doc(description="Get total revenue accumulated on each chain")
@api.response(404, "Chain or pool not found")
class RevenueByChain(Resource):
    @api.marshal_list_with(chain_rev, envelope="revenue")
    def get(self):
        return get_platform_revenue()
