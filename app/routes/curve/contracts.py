from flask_restx import Resource, Namespace

api = Namespace('contracts', description='Contracts endpoints')


@api.route('/<string:chain>/factories')
@api.doc(description="Get all historical factory contracts")
@api.param('chain', 'Chain to query for')
@api.response(404, 'Chain or pool not found')
class FactoryList(Resource):
    def get(self, chain, pool):
        print(chain)
        return pool


@api.route('/<string:chain>/registries')
@api.doc(description="Get all historcial registry contracts")
@api.param('chain', 'Chain to query for')
@api.response(404, 'Chain or pool not found')
class RegistryList(Resource):
    def get(self, chain, pool):
        print(chain)
        return pool


@api.route('/<string:chain>/gauges')
@api.doc(description="Get all historcial registry contracts")
@api.param('chain', 'Chain to query for')
@api.response(404, 'Chain or pool not found')
class GaugeList(Resource):
    def get(self, chain, pool):
        print(chain)
        return pool


