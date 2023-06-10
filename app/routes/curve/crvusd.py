from flask_restx import Resource, Namespace, fields, reqparse, Model
import json
from main import redis  # type: ignore

from models.curve.crvusd import (
    CrvUsdPoolStat,
    Histogram,
    MarketInfo,
    MarketRate,
    MarketVolume,
    MarketLoans,
    UserStateData,
)
from models.curve.pool import CurvePoolName
from services.curve.crvusd import (
    get_crv_usd_pool_names,
    get_crv_usd_pool_stats,
    get_crvusd_markets,
    get_hourly_market_rates,
    get_daily_market_rates,
    get_daily_market_volume,
    get_daily_market_loans,
    get_latest_user_states,
    get_user_health_histogram,
)
from utils import convert_schema

api = Namespace("crvusd", description="crvUSD endpoints")
names = api.model("Pool Name", convert_schema(CurvePoolName))
stats = api.model("Pool Stats", convert_schema(CrvUsdPoolStat))
hist = api.model("Histogram", convert_schema(Histogram))
markets = api.model("Market descriptions", convert_schema(MarketInfo))
wild = fields.Wildcard(fields.Float)
prices = api.model("crvUSD prices", {"timestamp": fields.Integer, "*": wild})
rates = api.model("Market historical rates", convert_schema(MarketRate))
volume = api.model("Market historical volume", convert_schema(MarketVolume))
loans = api.model("Market historical loan number", convert_schema(MarketLoans))
states = api.model("User states", convert_schema(UserStateData))
interval_data_model = api.model(
    "IntervalData",
    {
        "debt": fields.Float,
        "collateral": fields.Float,
        "collateralUsd": fields.Float,
        "stableCoin": fields.Float,
    },
)
deciles = api.model(
    "Health ratio deciles",
    {"*": fields.Wildcard(fields.Nested(interval_data_model))},
)
pagination = reqparse.RequestParser()
pagination.add_argument(
    "offset",
    type=int,
    help="Offset (for pagination)",
    required=True,
    location="args",
)
pagination.add_argument(
    "limit",
    type=int,
    help="Limit (for pagination)",
    required=True,
    location="args",
)


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


@api.route('/markets/<regex("[A-z0-9]+"):market>/rate/hourly')
@api.doc(description="Get historical hourly rate over past 5 days")
@api.param("market", "Market to query for")
class MarketHourlyRate(Resource):
    @api.marshal_list_with(rates, envelope="rates")
    def get(self, market):
        return get_hourly_market_rates(market)


@api.route('/markets/<regex("[A-z0-9]+"):market>/rate/daily')
@api.doc(description="Get average daily rate history")
@api.param("market", "Market to query for")
class MarketDailyRate(Resource):
    @api.marshal_list_with(rates, envelope="rates")
    def get(self, market):
        return get_daily_market_rates(market)


@api.route('/markets/<regex("[A-z0-9]+"):market>/volume')
@api.doc(description="Get market trading volume history")
@api.param("market", "Market to query for")
class DailyMarketVolume(Resource):
    @api.marshal_list_with(volume, envelope="volumes")
    def get(self, market):
        return get_daily_market_volume(market)


@api.route('/markets/<regex("[A-z0-9]+"):market>/loans')
@api.doc(description="Get daily loan # history")
@api.param("market", "Market to query for")
class DailyMarketLoans(Resource):
    @api.marshal_list_with(loans, envelope="loans")
    def get(self, market):
        return get_daily_market_loans(market)


@api.route('/markets/<regex("[A-z0-9]+"):market>/users/states')
@api.doc(description="Get latest user states")
@api.param("market", "Market to query for")
@api.expect(pagination)
class UserRecentStates(Resource):
    @api.marshal_list_with(states, envelope="states")
    def get(self, market):
        args = pagination.parse_args()
        return get_latest_user_states(market, **args)


@api.route('/markets/<regex("[A-z0-9]+"):market>/users/health/deciles')
@api.doc(description="Get histogram of users health ratio")
@api.param("market", "Market to query for")
class UserHealthDeciles(Resource):
    @api.marshal_list_with(deciles, envelope="deciles")
    def get(self, market):
        return get_user_health_histogram(market)
