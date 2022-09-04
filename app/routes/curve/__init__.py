from flask import Blueprint
from flask_restx import Api
from routes.curve.pools import api as pool_ns
from routes.curve.protocol import api as protocol_ns


crv_blueprint = Blueprint("curve", __name__, url_prefix="/curve/v1")
api = Api(
    crv_blueprint,
    title="Curve API",
    version="1.0",
    description="Endpoints for Curve analytics",
    doc="/docs",
)
api.add_namespace(protocol_ns)
api.add_namespace(pool_ns)
