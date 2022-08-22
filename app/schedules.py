from celery.schedules import crontab


CELERY_IMPORTS = ('tasks.populate')
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE = {
    'populate-db': {
        'task': 'tasks.populate.populate_db',
        'schedule': crontab(minute="*"),
    }
}