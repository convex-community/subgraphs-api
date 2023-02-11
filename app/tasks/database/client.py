import os
import sys
import logging
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from celery.utils.log import get_task_logger

cosmos_logger = logging.getLogger("azure")
cosmos_logger.setLevel(logging.WARNING)
handler = logging.StreamHandler(stream=sys.stdout)
cosmos_logger.addHandler(handler)

logger = get_task_logger(__name__)


def get_database():
    db_endpoint = os.getenv("DB_ENDPOINT")
    db_key = os.getenv("DB_KEY")
    db_name = os.getenv("DB_NAME")
    client = CosmosClient(db_endpoint, credential=db_key, logging_enable=True)

    try:
        database = client.create_database(db_name)
        logger.info(f"Database {db_name} created.")
    except exceptions.CosmosResourceExistsError:
        database = client.get_database_client(db_name)
        logger.info(f"Connected to {db_name}.")
    return database


def get_container(container_name, clear_existing=False):
    database = get_database()
    if clear_existing:
        try:
            database.delete_container(
                container_name, partition_key=PartitionKey(path="/id")
            )
        except Exception as e:
            logger.warning(e)

    try:
        container = database.create_container(
            id=container_name, partition_key=PartitionKey(path="/id")
        )
    except exceptions.CosmosResourceExistsError:
        container = database.get_container_client(container_name)
    except exceptions.CosmosHttpResponseError:
        raise
    return container
