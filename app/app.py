import os
from flask_restx import Api
from main import create_app
from tasks.celery import make_celery
from routes.curve import crv_blueprint
import schedules
from strawberry.flask.views import GraphQLView
from graphq.schema import schema

app = create_app(os.getenv('SUBGRAPHS_API_ENV') or 'dev')
app.app_context().push()
app.register_blueprint(crv_blueprint)

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql_view", schema=schema),
)

api = Api(app=app, doc='/docs')
celery = make_celery(app)
celery.config_from_object(schedules)


if __name__ == '__main__':
    app.run()