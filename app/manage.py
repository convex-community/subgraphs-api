import os
from flask_restx import Api
from main import create_app
from tasks.celery import make_celery
from routes.curve import crv_blueprint
import schedules


app = create_app(os.getenv('SUBGRAPHS_API_ENV') or 'dev')
app.app_context().push()
app.register_blueprint(crv_blueprint)
api = Api(app=app, doc='/docs')
celery = make_celery(app)
celery.config_from_object(schedules)


if __name__ == '__main__':
    app.run()