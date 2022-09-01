import os
from flask_restx import Api
from main import create_app
from tasks.celery import make_celery
import schedules
from strawberry.flask.views import GraphQLView
from graphq.schema import schema
from utils import RegexConverter
from flask_caching import Cache


app = create_app(os.getenv('API_ENV') or 'dev')
app.app_context().push()
app.url_map.converters['regex'] = RegexConverter

app.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view("graphql_view", schema=schema),
)

api = Api(app=app, doc='/docs')
celery = make_celery(app)
celery.config_from_object(schedules)
cache = Cache(app)


if __name__ == '__main__':
    app.run()