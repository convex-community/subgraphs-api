from manage import celery


@celery.task
def populate_db():
    print("Populated")