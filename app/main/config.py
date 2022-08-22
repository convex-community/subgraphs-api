import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    ALCHEMY_KEY = os.getenv('WEB3_ALCHEMY_API_KEY', 'test')
    DEBUG = False
    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    MAINNET_SUBGRAPH_ENDPOINT = "a"


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    MAINNET_SUBGRAPH_ENDPOINT = "b"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    MAINNET_SUBGRAPH_ENDPOINT = "c"


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.ALCHEMY_KEY