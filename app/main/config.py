import os
from main.const import SUBGRAPHS_DEV, SUBGRAPHS_PROD

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    ALCHEMY_KEY = os.getenv('WEB3_ALCHEMY_API_KEY', 'test')
    DEBUG = False
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379')
    DB_ENDPOINT = os.getenv('DB_ENDPOINT')
    DB_KEY = os.getenv('DB_KEY')
    DB_NAME = os.getenv('DB_NAME')
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv('CACHE_REDIS_URL', 'redis://localhost:6379')
    CACHE_DEFAULT_TIMEOUT = 60 * 60 * 12


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SUBGRAPHS = SUBGRAPHS_DEV


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SUBGRAPHS = SUBGRAPHS_DEV


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SUBGRAPHS = SUBGRAPHS_PROD


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.ALCHEMY_KEY