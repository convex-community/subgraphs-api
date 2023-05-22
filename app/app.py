import os
from flask_restx import Api
from main import create_app
from routes.curve import crv_blueprint
from routes.convex import cvx_blueprint
from routes import cache
from tasks.celery import make_celery
import schedules
from utils import RegexConverter
from flask_cors import CORS


app = create_app(os.getenv("API_ENV") or "dev")
app.app_context().push()
app.url_map.converters["regex"] = RegexConverter
cache.init_app(app)
# with app.app_context():
#    cache.clear()

api = Api(app=app, doc="/docs")
celery = make_celery(app)
celery.config_from_object(schedules)
app.register_blueprint(cvx_blueprint)
app.register_blueprint(crv_blueprint)
CORS(app)


if __name__ == "__main__":
    app.run()
