from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from redis import Redis  # type: ignore
from .config import config_by_name
import os

db = SQLAlchemy()
migrate = Migrate()
redis = Redis(
    host="redis", password=os.getenv("REDIS_PASSWORD", ""), port=6379, db=0
)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    db.init_app(app)
    migrate.init_app(app, db)
    return app
