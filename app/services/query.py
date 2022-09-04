import os
import sys
import logging
from flask import g
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from celery.utils.log import get_task_logger

cosmos_logger = logging.getLogger("azure")
cosmos_logger.setLevel(logging.WARNING)
handler = logging.StreamHandler(stream=sys.stdout)
cosmos_logger.addHandler(handler)

logger = get_task_logger(__name__)


def get_database():
    if not hasattr(g, "db"):
        db_endpoint = os.getenv("DB_ENDPOINT", "")
        db_key = os.getenv("DB_KEY", "")
        db_name = os.getenv("DB_NAME", "")
        client = CosmosClient(
            db_endpoint, credential=db_key, logging_enable=True
        )

        try:
            database = client.create_database(db_name)
            logger.info(f"Database {db_name} created.")
        except exceptions.CosmosResourceExistsError:
            database = client.get_database_client(db_name)
            logger.info(f"Connected to {db_name}.")
        setattr(g, "db", database)
    return getattr(g, "db")


def get_container(container_name):
    database = get_database()
    if not hasattr(g, f"ctnr_{container_name}"):
        try:
            container = database.create_container(
                id=container_name, partition_key=PartitionKey(path="/id")
            )
        except exceptions.CosmosResourceExistsError:
            container = database.get_container_client(container_name)
        except exceptions.CosmosHttpResponseError:
            raise
        setattr(g, f"ctnr_{container_name}", container)
    return getattr(g, f"ctnr_{container_name}")


def query_db(container, query: str):
    results = [
        item
        for item in container.query_items(
            query=query, enable_cross_partition_query=True
        )
    ]
    return results
