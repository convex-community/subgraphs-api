from flask import Blueprint
from flask_restx import Api
from routes.convex.pools import api as pool_ns
from app import app


cvx_blueprint = Blueprint('convex', __name__, url_prefix='/convex/v1')
api = Api(cvx_blueprint, title="Convex API", version="1.0", description="Endpoints for Convex analytics", doc="/docs")
api.add_namespace(pool_ns)
app.register_blueprint(cvx_blueprint)