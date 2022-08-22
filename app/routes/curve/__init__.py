from flask import Blueprint
from flask_restx import Api
from .pools import api as pool_ns
from .contracts import api as contract_ns


crv_blueprint = Blueprint('curve', __name__, url_prefix='/curve/v1')
api = Api(crv_blueprint, title="Curve API", version="1.0", description="Endpoints for Curve analytics", doc="/docs")
api.add_namespace(contract_ns)
api.add_namespace(pool_ns)
