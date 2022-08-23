from celery.schedules import crontab
from main.const import CHAINS


imports = ('tasks.populate')
result_expires = 30
timezone = 'UTC'

accept_content = ['json', 'msgpack', 'yaml']
task_serializer = 'json'
result_serializer = 'json'

curve_pool_tasks = {
    f"populate-curve-pools-{chain}": {
        'task': 'tasks.populate.populate_curve_pools',
        'schedule': crontab(minute="*/15"),
        'args': (chain,)
    } for chain in CHAINS
}

beat_schedule = curve_pool_tasks
