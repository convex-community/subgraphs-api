import time

from flask import request
from flask_restx import Resource, Namespace, fields, reqparse, Model, marshal
import json
from routes import cache
from main import redis  # type: ignore

from models.curve.crvusd import (
    CrvUsdPoolStat,
    Histogram,
    MarketInfo,
    MarketRate,
    MarketVolume,
    MarketLoans,
    UserStateData,
    TotalSupply,
    KeepersDebt,
    CrvUsdFees,
    CrvUsdFeesBreakdown,
    KeepersProfit,
    CrvUsdYield,
    HistoricalKeeperDebtData,
    MarketLosers,
    HistoricalMarketLosers,
    HistoricalMedianLoss,
    HistoricalSoftLoss,
    HealthDistribution,
    HistoricalLiquidations,
    AggregatedLiquidations,
    Liquidators,
    HistoricalHealth,
    MarketHealthState,
    SupplyAvailable,
    LiquidatorRevenue,
    CollateralRatios,
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
    get_historical_supply,
    get_keepers_debt,
    get_historical_keeper_debt_data,
    get_aggregated_fees,
    get_fees_breakdown,
    get_keepers_profit,
    get_volume_snapshot,
    get_market_borrowable,
)
from services.curve.liquidations import (
    get_loser_proportions,
    get_historical_loser_proportions,
    get_historical_median_loss,
    get_historical_soft_loss,
    get_health_distribution,
    get_liquidation_history,
    get_aggregated_liquidations,
    get_top_liquidators,
    get_historical_health,
    get_market_health,
    get_liquidator_revenue,
    get_collateral_ratio,
)
from services.curve.yields import get_crv_usd_yields
from utils import convert_schema

api = Namespace("crvusd", description="crvUSD endpoints")
names = api.model("Pool Name", convert_schema(CurvePoolName))
stats = api.model("Pool Stats", convert_schema(CrvUsdPoolStat))
hist = api.model("Histogram", convert_schema(Histogram))
markets = api.model("Market descriptions", convert_schema(MarketInfo))
wild = fields.Wildcard(fields.Float)
prices = api.model("crvUSD prices", {"timestamp": fields.Integer, "*": wild})
rates = api.model("Market historical rates", convert_schema(MarketRate))
fees = api.model("Pending and collected fees", convert_schema(CrvUsdFees))
breakdown = api.model("Fee breakdown", convert_schema(CrvUsdFeesBreakdown))
detailed_fees = api.model(
    "Breakdown of pending and collected fees",
    {
        "pending": fields.Nested(breakdown),
        "collected": fields.Nested(breakdown),
    },
)
volume = api.model("Market historical volume", convert_schema(MarketVolume))
loans = api.model("Market historical loan number", convert_schema(MarketLoans))
losers = api.model(
    "Proportion of users with losses", convert_schema(MarketLosers)
)
historical_losers = api.model(
    "Historical proportion of users with losses",
    convert_schema(HistoricalMarketLosers),
)
historical_median_loss = api.model(
    "Historical median loss % of users with losses",
    convert_schema(HistoricalMedianLoss),
)
historical_soft_loss = api.model(
    "Historical % of users in soft liquidation",
    convert_schema(HistoricalSoftLoss),
)
historical_health = api.model(
    "Median health of users",
    convert_schema(HistoricalHealth),
)
health_distribution = api.model(
    "Debt & collateral value in health deciles",
    convert_schema(HealthDistribution),
)
liquidation_history = api.model(
    "Historical liquidation count and details per day",
    convert_schema(HistoricalLiquidations),
)
aggregated_liquidations = api.model(
    "Aggregated liquidation count and details",
    convert_schema(AggregatedLiquidations),
)
liquidators = api.model(
    "Top liquidators stats",
    convert_schema(Liquidators),
)
liquidators_revenue = api.model(
    "Liquidator Revenue",
    convert_schema(LiquidatorRevenue),
)
health_state = api.model(
    "General market health stats",
    convert_schema(MarketHealthState),
)
states = api.model("User states", convert_schema(UserStateData))
supply_available = api.model(
    "Stablecoin available to borrow", convert_schema(SupplyAvailable)
)
cratio = api.model("Collateral ratio", convert_schema(CollateralRatios))
keepers_debt = api.model("Keepers debt", convert_schema(KeepersDebt))
historical_keepers_debt = api.model(
    "Historical Keepers debt", convert_schema(HistoricalKeeperDebtData)
)
keepers_profit = api.model("Keepers profit", convert_schema(KeepersProfit))
interval_data_model = api.model(
    "IntervalData",
    {
        "debt": fields.Float,
        "collateral": fields.Float,
        "collateralUsd": fields.Float,
        "stableCoin": fields.Float,
    },
)
supply = api.model("crvUSD historical supply", convert_schema(TotalSupply))
yields = api.model("crvUSD yield opportunities", convert_schema(CrvUsdYield))

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

snapshot = reqparse.RequestParser()
snapshot.add_argument(
    "period",
    type=int,
    choices=(3600, 86400),
    help="Period (in seconds)",
    required=True,
    location="args",
)
snapshot.add_argument(
    "start_date",
    type=int,
    help="Starting date",
    default=0,
    location="args",
)
snapshot.add_argument(
    "end_date",
    type=int,
    help="End date",
    default=int(time.time()),
    location="args",
)

days_parser = reqparse.RequestParser()
days_parser.add_argument(
    "days",
    type=int,
    help="Number of days to retrieve",
    default=30,
    location="args",
)


@api.route("/pools")
@api.doc(description="Get the crvUSD pools")
class PoolList(Resource):
    @cache.cached(timeout=60 * 3)
    @api.marshal_list_with(names, envelope="pools")
    def get(self):
        return get_crv_usd_pool_names()


@api.route("/pools/stats")
@api.doc(description="Get descriptive stats for crvUSD pools")
class PoolStats(Resource):
    @cache.cached(timeout=60 * 3)
    @api.marshal_list_with(stats, envelope="stats")
    def get(self):
        return get_crv_usd_pool_stats()


@api.route("/prices")
@api.doc(description="Get historical prices for crvUSD pools")
class UsdPrices(Resource):
    @cache.cached(timeout=60 * 3)
    @api.marshal_list_with(prices, envelope="prices")
    def get(self):
        return json.loads(redis.get("crvusd_prices"))


@api.route("/supply")
@api.doc(description="Get historical supply for crvUSD")
class CrvUsdSupply(Resource):
    @cache.cached(timeout=60 * 3)
    @api.marshal_list_with(supply, envelope="supply")
    def get(self):
        return get_historical_supply()


@api.route("/keepers/debt")
@api.doc(description="Get Keepers debt breakdown")
class DebtOfKeepers(Resource):
    @api.marshal_list_with(keepers_debt, envelope="keepers")
    def get(self):
        return get_keepers_debt()


@api.route('/keepers/debt/historical/<regex("[A-z0-9]+"):keeper>')
@api.doc(description="Get historical keeper's debt")
@api.param("keeper", "Address of the Keeper to query for")
class HistoricalDebtOfKeepers(Resource):
    @api.expect(days_parser)
    @api.marshal_list_with(historical_keepers_debt, envelope="keepers")
    def get(self, keeper):
        days = int(request.args.get("days", 30))
        return get_historical_keeper_debt_data(keeper, days)


@api.route("/keepers/profit")
@api.doc(description="Get Keepers total all-time profit")
class ProfitOfKeepers(Resource):
    @cache.cached(timeout=60 * 3)
    @api.marshal_list_with(keepers_profit, envelope="profit")
    def get(self):
        return get_keepers_profit()


@api.route("/prices/hist")
@api.doc(description="Get crvUSD USD price histogram")
class PricesHist(Resource):
    @cache.cached(timeout=60 * 3)
    @api.marshal_with(hist)
    def get(self):
        return json.loads(redis.get("crvusd_hist"))


@api.route("/yield")
@api.doc(description="List all yield opportunities for crvusd staking")
class YieldList(Resource):
    @cache.cached(timeout=60)
    @api.marshal_list_with(yields, envelope="yields")
    def get(self):
        return get_crv_usd_yields()


@api.route("/markets")
@api.doc(description="List all markets and their descriptive stats")
class MarketList(Resource):
    @cache.cached(timeout=60 * 3)
    @api.marshal_list_with(markets, envelope="markets")
    def get(self):
        return get_crvusd_markets()


@api.route('/markets/summary/<regex("[A-z0-9]+"):market>')
@api.doc(description="Get a market's descriptive stats")
@api.param("market", "Market to query for")
class MarketDesc(Resource):
    @cache.cached(timeout=60 * 3)
    @api.marshal_list_with(markets, envelope="markets")
    def get(self, market):
        return get_crvusd_markets(market)


@api.route('/markets/<regex("[A-z0-9]+"):market>/rate/hourly')
@api.doc(description="Get historical hourly rate over past 5 days")
@api.param("market", "Market to query for")
class MarketHourlyRate(Resource):
    @cache.cached(timeout=60 * 3)
    @api.marshal_list_with(rates, envelope="rates")
    def get(self, market):
        return get_hourly_market_rates(market)


@api.route('/markets/<regex("[A-z0-9]+"):market>/rate/daily')
@api.doc(description="Get average daily rate history")
@api.param("market", "Market to query for")
class MarketDailyRate(Resource):
    @cache.cached(timeout=60 * 3)
    @api.marshal_list_with(rates, envelope="rates")
    def get(self, market):
        return get_daily_market_rates(market)


@api.route('/markets/<regex("[A-z0-9]+"):market>/volume')
@api.doc(description="Get market trading volume history")
@api.param("market", "Market to query for")
class DailyMarketVolume(Resource):
    @cache.cached(timeout=60 * 3)
    @api.marshal_list_with(volume, envelope="volumes")
    def get(self, market):
        return get_daily_market_volume(market)


@api.route('/markets/<regex("[A-z0-9]+"):market>/loans')
@api.doc(description="Get daily loan # history")
@api.param("market", "Market to query for")
class DailyMarketLoans(Resource):
    @cache.cached(timeout=60 * 3)
    @api.marshal_list_with(loans, envelope="loans")
    def get(self, market):
        return get_daily_market_loans(market)


@api.route('/markets/<regex("[A-z0-9]+"):market>/users/states')
@api.doc(description="Get latest user states")
@api.param("market", "Market to query for")
@api.expect(pagination)
class UserRecentStates(Resource):
    @cache.cached(timeout=60 * 3)
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


@api.route("/fees")
@api.doc(description="Get aggregated pending and collected fees")
class TotalFees(Resource):
    @cache.cached(timeout=60 * 3)
    @api.marshal_list_with(fees, envelope="fees")
    def get(self):
        return get_aggregated_fees()


@api.route('/markets/<regex("[A-z0-9]+"):market>/fees')
@api.doc(
    description="Get aggregated pending and collected fees for a specific market"
)
@api.param("market", "Market to query for")
class MarketTotalFees(Resource):
    @cache.cached(timeout=60 * 3)
    @api.marshal_list_with(fees, envelope="fees")
    def get(self, market):
        return get_aggregated_fees(market_id=market)


@api.route("/fees/breakdown")
@api.doc(description="Get breakdown of pending and collected fees")
class TotalDetailedFees(Resource):
    @cache.cached(timeout=60 * 3)
    @api.marshal_with(detailed_fees)
    def get(self):
        return get_fees_breakdown()


@api.route('/markets/<regex("[A-z0-9]+"):market>/fees/breakdown')
@api.doc(
    description="Get breakdown of pending and collected fees for a specific market"
)
@api.param("market", "Market to query for")
class MarketTotalDetailedFees(Resource):
    @cache.cached(timeout=60 * 15)
    @api.marshal_with(detailed_fees)
    def get(self, market):
        return get_fees_breakdown(market_id=market)


@api.route('/markets/<regex("[A-z0-9]+"):market>/volume/snapshots')
@api.doc(
    description="Get volume snapshots per period over specified dates for a market"
)
@api.param("market", "Market to query for")
@api.expect(snapshot)
class LlammaVolumeSnapshot(Resource):
    @cache.cached(timeout=60 * 15)
    @api.marshal_list_with(volume, envelope="volumes")
    def get(self, market):
        args = snapshot.parse_args()
        return get_volume_snapshot(market_id=market, **args)


@api.route("/markets/liquidations/losses/proportions")
@api.doc(description="Get proportion of users with losses for all market")
class MarketLossProportion(Resource):
    @cache.cached(timeout=60 * 15)
    @api.marshal_list_with(losers, envelope="losses")
    def get(self):
        return get_loser_proportions()


@api.route(
    '/markets/<regex("[A-z0-9]+"):market>/liquidations/losses/historical/proportions'
)
@api.doc(description="Get historical fraction of users with losses")
@api.param("market", "Market to query for")
class MarketHistoricLossProportion(Resource):
    @cache.cached(timeout=60 * 15)
    @api.marshal_list_with(historical_losers, envelope="losses")
    def get(self, market):
        res = get_historical_loser_proportions(market_id=market)
        if not res:
            api.abort(404)
        return res


@api.route(
    '/markets/<regex("[A-z0-9]+"):market>/liquidations/losses/historical/median'
)
@api.doc(description="Get historical median loss % of users with losses")
@api.param("market", "Market to query for")
class MarketHistoricMedianLosses(Resource):
    @cache.cached(timeout=60 * 10)
    @api.marshal_list_with(historical_median_loss, envelope="losses")
    def get(self, market):
        res = get_historical_median_loss(market_id=market)
        if not res:
            api.abort(404)
        return res


@api.route(
    '/markets/<regex("[A-z0-9]+"):market>/liquidations/losses/historical/soft'
)
@api.doc(description="Get historical proportion of users in soft liquidation")
@api.param("market", "Market to query for")
class MarketHistoricSoftLosses(Resource):
    @cache.cached(timeout=60 * 10)
    @api.marshal_list_with(historical_soft_loss, envelope="losses")
    def get(self, market):
        res = get_historical_soft_loss(market_id=market)
        if not res:
            api.abort(404)
        return res


@api.route(
    '/markets/<regex("[A-z0-9]+"):market>/liquidations/health/historical'
)
@api.doc(description="Get historical median health factor")
@api.param("market", "Market to query for")
class MarketHistoricHealth(Resource):
    @cache.cached(timeout=60 * 10)
    @api.marshal_list_with(historical_health, envelope="health")
    def get(self, market):
        res = get_historical_health(market_id=market)
        if not res:
            api.abort(404)
        return res


@api.route('/markets/<regex("[A-z0-9]+"):market>/liquidations/health')
@api.doc(description="Get collateral value & debt by health deciles ")
@api.param("market", "Market to query for")
class MarketHealthDistribution(Resource):
    @cache.cached(timeout=60 * 10)
    @api.marshal_list_with(health_distribution, envelope="health")
    def get(self, market):
        res = get_health_distribution(market_id=market)
        if not res:
            api.abort(404)
        return res


@api.route('/markets/<regex("[A-z0-9]+"):market>/liquidations/historical')
@api.doc(description="Get stats for historical liquidations ")
@api.param("market", "Market to query for")
class MarketLiquidationHistory(Resource):
    @cache.cached(timeout=60 * 15)
    @api.marshal_list_with(liquidation_history, envelope="liquidations")
    def get(self, market):
        res = get_liquidation_history(market_id=market)
        if not res:
            api.abort(404)
        return res


@api.route('/markets/<regex("[A-z0-9]+"):market>/liquidations/aggregated')
@api.doc(description="Get stats for liquidations ")
@api.param("market", "Market to query for")
class MarketAggregatedLiquidation(Resource):
    @cache.cached(timeout=60 * 15)
    @api.marshal_list_with(aggregated_liquidations, envelope="liquidations")
    def get(self, market):
        res = get_aggregated_liquidations(market_id=market)
        if not res:
            api.abort(404)
        return res


@api.route('/markets/<regex("[A-z0-9]+"):market>/liquidations/liquidators')
@api.doc(description="Get stats for top liquidators ")
@api.param("market", "Market to query for")
class MarketTopLiquidators(Resource):
    @cache.cached(timeout=60 * 15)
    @api.marshal_list_with(liquidators, envelope="liquidations")
    def get(self, market):
        res = get_top_liquidators(market_id=market)
        if not res:
            api.abort(404)
        return res


@api.route(
    '/markets/<regex("[A-z0-9]+"):market>/liquidations/liquidators/revenue'
)
@api.doc(description="Get historical revenue of liquidators ")
@api.param("market", "Market to query for")
class MarketLiquidatorsRevenue(Resource):
    @api.marshal_list_with(liquidators_revenue, envelope="revenue")
    def get(self, market):
        res = get_liquidator_revenue(market_id=market)
        if not res:
            api.abort(404)
        return res


@api.route('/markets/<regex("[A-z0-9]+"):market>/liquidations/state')
@api.doc(description="Get stats for general market health ")
@api.param("market", "Market to query for")
class MarketLiqStates(Resource):
    @cache.cached(timeout=60 * 15)
    @api.marshal_list_with(health_state, envelope="health")
    def get(self, market):
        res = get_market_health(market_id=market)
        if not res:
            api.abort(404)
        return res


@api.route('/markets/<regex("[A-z0-9]+"):market>/available')
@api.doc(
    description="Get stablecoin available to borrow for a specific market"
)
@api.param("market", "Market to query for")
class MarketAvailable(Resource):
    @api.marshal_list_with(supply_available, envelope="available")
    def get(self, market):
        res = get_market_borrowable(market_id=market)
        if not res:
            api.abort(404)
        return res


@api.route('/markets/<regex("[A-z0-9]+"):market>/collateral_ratio')
@api.doc(description="Get historical collateral ratio for a specific market")
@api.param("market", "Market to query for")
class MarketCollatRatio(Resource):
    @api.marshal_list_with(cratio, envelope="ratios")
    def get(self, market):
        res = get_collateral_ratio(market_id=market)
        if not res:
            api.abort(404)
        return res
