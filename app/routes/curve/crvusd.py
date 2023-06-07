from flask_restx import Resource, Namespace, fields
import json
from main import redis  # type: ignore

from models.curve.crvusd import (
    CrvUsdPoolStat,
    CrvUsdPriceHistogram,
    MarketInfo,
)
from models.curve.pool import CurvePoolName
from services.curve.crvusd import (
    get_crv_usd_pool_names,
    get_crv_usd_pool_stats,
    get_crvusd_markets,
)
from utils import convert_schema

api = Namespace("crvusd", description="crvUSD endpoints")
names = api.model("Pool Name", convert_schema(CurvePoolName))
stats = api.model("Pool Stats", convert_schema(CrvUsdPoolStat))
hist = api.model("Price histogram", convert_schema(CrvUsdPriceHistogram))
markets = api.model("Market descriptions", convert_schema(MarketInfo))
wild = fields.Wildcard(fields.Float)
prices = api.model("crvUSD prices", {"timestamp": fields.Integer, "*": wild})


@api.route("/pools")
@api.doc(description="Get the crvUSD pools")
class PoolList(Resource):
    @api.marshal_list_with(names, envelope="pools")
    def get(self):
        return get_crv_usd_pool_names()


@api.route("/pools/stats")
@api.doc(description="Get descriptive stats for crvUSD pools")
class PoolStats(Resource):
    @api.marshal_list_with(stats, envelope="stats")
    def get(self):
        return get_crv_usd_pool_stats()


@api.route("/prices")
@api.doc(description="Get historical prices for crvUSD pools")
class UsdPrices(Resource):
    @api.marshal_list_with(prices, envelope="prices")
    def get(self):
        return json.loads(redis.get("crvusd_prices"))


@api.route("/prices/hist")
@api.doc(description="Get crvUSD USD price histogram")
class PricesHist(Resource):
    @api.marshal_with(hist)
    def get(self):
        return json.loads(redis.get("crvusd_hist"))


@api.route("/markets")
@api.doc(description="List all markets and their descriptive stats")
class MarketList(Resource):
    @api.marshal_list_with(markets, envelope="markets")
    def get(self):
        return get_crvusd_markets()
