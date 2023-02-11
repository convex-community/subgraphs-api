from flask_restx import Resource, Namespace, reqparse
from routes import cache
from models.convex.revenue import (
    ConvexCumulativeRevenue,
    ConvexRevenueSnapshot,
)
from services.convex.revenue import (
    get_platform_revenue_snapshots,
    get_platform_total_revenue,
)
from utils import convert_marshmallow


api = Namespace("platform", description="Platform endpoints")
total_rev = api.model(
    "Platform Total Revenue", convert_marshmallow(ConvexCumulativeRevenue)
)
rev_snapshots = api.model(
    "Platform Revenue Snapshots",
    convert_marshmallow(ConvexRevenueSnapshot),
)

revenue_parser = reqparse.RequestParser()
revenue_parser.add_argument(
    "groupby",
    type=str,
    choices=("d", "w", "m", "y"),
    help="Group revenue data by day, week, month or year. Possible values: 'd', 'w', 'm', 'y' ",
    required=True,
    location="args",
)


def check_exists(func):
    def wrapped(*args, **kwargs):
        data = func(*args, **kwargs)
        if not data:
            api.abort(404)
        return data

    return wrapped


@api.route("/revenue")
@api.doc(description="Get all time platform revenue")
class CumulativeRevenue(Resource):
    @api.marshal_list_with(total_rev, envelope="revenue")
    @cache.cached()
    def get(self):
        return get_platform_total_revenue()


@api.route("/revenue/snapshots")
@api.doc(description="Get historical platform revenue")
@api.expect(revenue_parser)
class RevenueSnapshots(Resource):
    @api.marshal_list_with(rev_snapshots, envelope="revenue")
    @cache.cached()
    def get(self):
        args = revenue_parser.parse_args()
        return get_platform_revenue_snapshots(**args)
