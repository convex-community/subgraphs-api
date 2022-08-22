from flask_restx import Resource, Namespace

api = Namespace('pools', description='Pools endpoints')


@api.route('/<string:chain>/')
@api.doc(description="Get all pool addresses")
@api.response(404, 'Chain or pool not found')
class PoolList(Resource):
    def get(self, chain):
        print(chain)
        return chain


@api.route('/<string:chain>/<string:pool>')
@api.doc(description="Get pool description")
@api.param('chain', 'Chain to query for')
@api.param('pool', 'Pool to query volume for')
@api.response(404, 'Chain or pool not found')
class Pool(Resource):
    def get(self, chain, pool):
        print(chain)
        return pool


@api.route('/<string:chain>/snapshots/<string:pool>')
@api.doc(description="Get historical pool snapshots")
@api.param('chain', 'Chain to query for')
@api.param('pool', 'Pool to query volume for')
@api.response(404, 'Chain or pool not found')
class PoolSnapshots(Resource):
    def get(self, chain, pool):
        print(chain)
        return pool


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
@api.doc(description="Get pool volume snapshots")
@api.param('chain', 'Chain to query for')
@api.param('pool', 'Pool to query volume for')
@api.response(404, 'Chain or pool not found')
class PoolVolume(Resource):
    def get(self, chain, pool):
        print(chain)
        return pool


@api.route('/<string:chain>/emissions/<string:pool>')
@api.doc(description="Get pool emissions")
@api.param('chain', 'Chain to query for')
@api.param('pool', 'Pool to query volume for')
@api.response(404, 'Chain or pool not found')
class PoolEmissions(Resource):
    def get(self, chain, pool):
        print(chain)
        return pool
