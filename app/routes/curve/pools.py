from flask_restx import Resource, Namespace

from main.const import CHAINS
from models.curve.snapshot import CurvePoolSnapshot, CurvePoolVolumeSnapshot, CurvePoolFeeSnapshot, \
    CurvePoolTVLSnapshot, CurvePoolReserveSnapshot
from services.curve.snapshot import get_pool_snapshots, get_pool_volume_snapshots, get_pool_fee_snapshots, \
    get_pool_reserves_snapshots, get_pool_tvl_snapshots
from utils import convert_marshmallow
from models.curve.pool import CurvePoolName, CurvePool
from services.curve.pool import get_pool_names, get_all_pool_metadata, get_pool_metadata

api = Namespace('pools', description='Pools endpoints')
names = api.model("Pool Name", convert_marshmallow(CurvePoolName))
metadata = api.model("Pool Metadata", convert_marshmallow(CurvePool))
snapshots = api.model("Pool Snapshot", convert_marshmallow(CurvePoolSnapshot))
volume = api.model("Pool Volume", convert_marshmallow(CurvePoolVolumeSnapshot))
fees = api.model("Pool Fees", convert_marshmallow(CurvePoolFeeSnapshot))
tvl = api.model("Pool TVL", convert_marshmallow(CurvePoolTVLSnapshot))
reserves = api.model("Pool Reserves", convert_marshmallow(CurvePoolReserveSnapshot))


def check_exists(func):
    def wrapped(*args, **kwargs):
        if kwargs['chain'] not in CHAINS:
            api.abort(404)
        data = func(*args, **kwargs)
        if not data:
            api.abort(404)
        return data
    return wrapped


@api.route('/<string:chain>/')
@api.doc(description="Get all pool names & addresses")
@api.response(404, 'Chain or pool not found')
class PoolList(Resource):
    @api.marshal_list_with(names,
                           envelope='pools')
    @check_exists
    def get(self, chain):
        return get_pool_names(chain)


@api.route('/<string:chain>/all')
@api.doc(description="Get all pools' metadata")
@api.response(404, 'Chain or pool not found')
class PoolMetadata(Resource):
    @api.marshal_list_with(metadata,
                           envelope='pools')
    @check_exists
    def get(self, chain):
        return get_all_pool_metadata(chain)


@api.route('/<string:chain>/<string:pool>')
@api.doc(description="Get pool metadata")
@api.param('chain', 'Chain to query for')
@api.param('pool', 'Pool to query volume for')
@api.response(404, 'Chain or pool not found')
class Pool(Resource):
    @api.marshal_with(metadata, envelope='pools')
    @check_exists
    def get(self, chain, pool):
        return get_pool_metadata(chain, pool)


@api.route('/<string:chain>/snapshots/<string:pool>')
@api.doc(description="Get historical pool snapshots")
@api.param('chain', 'Chain to query for')
@api.param('pool', 'Pool to query volume for')
@api.response(404, 'Chain or pool not found')
class PoolSnapshots(Resource):
    @api.marshal_list_with(snapshots, envelope='snapshots')
    @check_exists
    def get(self, chain, pool):
        return get_pool_snapshots(chain, pool)


@api.route('/<string:chain>/swaps/<string:pool>')
@api.doc(description="Get pool swap events")
@api.param('chain', 'Chain to query for')
@api.param('pool', 'Pool to query volume for')
@api.response(404, 'Chain or pool not found')
class PoolSwaps(Resource):
    def get(self, chain, pool):
        print(chain)
        return pool


@api.route('/<string:chain>/candles/<string:pool>')
@api.doc(description="Get pool price candles")
@api.param('chain', 'Chain to query for')
@api.param('pool', 'Pool to query volume for')
@api.response(404, 'Chain or pool not found')
class PoolCandles(Resource):
    def get(self, chain, pool):
        print(chain)
        return pool


@api.route('/<string:chain>/volume/<string:pool>')
@api.doc(description="Get historical pool volume")
@api.param('chain', 'Chain to query for')
@api.param('pool', 'Pool to query volume for')
@api.response(404, 'Chain or pool not found')
class PoolVolume(Resource):
    @api.marshal_list_with(volume, envelope='volume')
    @check_exists
    def get(self, chain, pool):
        return get_pool_volume_snapshots(chain, pool)


@api.route('/<string:chain>/fees/<string:pool>')
@api.doc(description="Get historical pool fees")
@api.param('chain', 'Chain to query for')
@api.param('pool', 'Pool to query fees for')
@api.response(404, 'Chain or pool not found')
class PoolFees(Resource):
    @api.marshal_list_with(fees, envelope='fees')
    @check_exists
    def get(self, chain, pool):
        return get_pool_fee_snapshots(chain, pool)


@api.route('/<string:chain>/reserves/<string:pool>')
@api.doc(description="Get historical pool reserves")
@api.param('chain', 'Chain to query for')
@api.param('pool', 'Pool to query reserves for')
@api.response(404, 'Chain or pool not found')
class PoolReserves(Resource):
    @api.marshal_list_with(reserves, envelope='reserves')
    @check_exists
    def get(self, chain, pool):
        return get_pool_reserves_snapshots(chain, pool)


@api.route('/<string:chain>/tvl/<string:pool>')
@api.doc(description="Get historical pool TVL")
@api.param('chain', 'Chain to query for')
@api.param('pool', 'Pool to query TVL for')
@api.response(404, 'Chain or pool not found')
class PoolValue(Resource):
    @api.marshal_list_with(tvl, envelope='tvl')
    @check_exists
    def get(self, chain, pool):
        return get_pool_tvl_snapshots(chain, pool)


@api.route('/<string:chain>/emissions/<string:pool>')
@api.doc(description="Get pool emissions")
@api.param('chain', 'Chain to query for')
@api.param('pool', 'Pool to query volume for')
@api.response(404, 'Chain or pool not found')
class PoolEmissions(Resource):
    def get(self, chain, pool):
        print(chain)
        return pool
