from flask_restx import Resource, Namespace

from utils import convert_marshmallow
from models.convex.pool import ConvexPool
from services.convex.pool import get_all_pool_metadata

api = Namespace('pools', description='Pools endpoints')
metadata = api.model("Pool Metadata", convert_marshmallow(ConvexPool))


def check_exists(func):
    def wrapped(*args, **kwargs):
        data = func(*args, **kwargs)
        if not data:
            api.abort(404)
        return data
    return wrapped


@api.route('/all')
@api.doc(description="Get all pools' metadata")
@api.response(404, 'Chain or pool not found')
class PoolMetadata(Resource):
    @api.marshal_list_with(metadata,
                           envelope='pools')
    @check_exists
    def get(self):
        data = get_all_pool_metadata()
        if not data:
            api.abort(404)
        return data
