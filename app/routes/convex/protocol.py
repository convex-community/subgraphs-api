from flask_restx import Resource, Namespace
from routes import cache
from models.convex.revenue import ConvexCumulativeRevenue, ConvexHistoricalRevenueSnapshot
from services.convex.revenue import get_platform_revenue_snapshots, get_platform_total_revenue
from utils import convert_marshmallow


api = Namespace('platform', description='Platform endpoints')
total_rev = api.model("Platform Total Revenue", convert_marshmallow(ConvexCumulativeRevenue))
rev_snapshots = api.model("Platform Revenue Snapshots", convert_marshmallow(ConvexHistoricalRevenueSnapshot))


def check_exists(func):
    def wrapped(*args, **kwargs):
        data = func(*args, **kwargs)
        if not data:
            api.abort(404)
        return data
    return wrapped


@api.route('/revenue')
@api.doc(description="Get all time platform revenue")
@api.response(404, 'Pool not found')
class CumulativeRevenue(Resource):
    @api.marshal_list_with(total_rev,
                           envelope='revenue')
    @cache.cached()
    @check_exists
    def get(self):
        return get_platform_total_revenue()


@api.route('/revenue/snapshots')
@api.doc(description="Get historical platform revenue")
@api.response(404, 'Pool not found')
class RevenueSnapshots(Resource):
    @api.marshal_list_with(rev_snapshots,
                           envelope='revenue')
    @cache.cached()
    @check_exists
    def get(self):
        return get_platform_revenue_snapshots()