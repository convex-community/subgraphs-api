from flask_restx import Resource, Namespace, fields

from main.const import CHAINS
from models.curve.revenue import (
    CurveChainRevenue,
    CurveHistoricalPoolCumulativeRevenue,
    CurveChainTopPoolRevenue,
)
from routes import cache
from services.curve.revenue import (
    get_platform_revenue,
    get_top_pools,
    get_top_chain_pools,
)
from utils import convert_marshmallow

api = Namespace("protocol", description="Protocol endpoints")
chain_rev = api.model("Chain Revenue", convert_marshmallow(CurveChainRevenue))
top_pools = api.model(
    "Top Pools", convert_marshmallow(CurveHistoricalPoolCumulativeRevenue)
)
chain_top_pools = api.model(
    "Chain Top Pools", convert_marshmallow(CurveChainTopPoolRevenue)
)
chains = api.model("Supported Chains", {"chains": fields.List(fields.String)})


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


@api.route("/<string:chain>/gauges")
@api.doc(description="Get all historcial registry contracts")
@api.param("chain", "Chain to query for")
@api.response(404, "Chain or pool not found")
class GaugeList(Resource):
    def get(self, chain, pool):
        print(chain)
        return pool


@api.route("/revenue/historical/toppools/<int:top>")
@api.doc(description="Get weekly revenue of top pools vs others")
@api.param("top", "Number of top pools to single out")
@api.response(404, "Not found")
class TopPoolList(Resource):
    @cache.cached()
    @api.marshal_list_with(top_pools, envelope="revenue")
    def get(self, top):
        return get_top_pools(top)


@api.route("/revenue/<string:chain>/toppools/<int:top>")
@api.doc(description="Get top pools by revenue for a chain for previous week")
@api.param("chain", "Name of the chain to query for")
@api.response(404, "Not found")
class ChainTopPoolList(Resource):
    @cache.cached()
    @api.marshal_list_with(chain_top_pools, envelope="revenue")
    def get(self, chain, top):
        return get_top_chain_pools(chain, top)


@api.route("/revenue/chains")
@api.doc(description="Get total revenue accumulated on each chain")
@api.response(404, "Chain or pool not found")
class RevenueByChain(Resource):
    @cache.cached()
    @api.marshal_list_with(chain_rev, envelope="revenue")
    def get(self):
        return get_platform_revenue()
