from celery.schedules import crontab
from main.const import CHAINS


imports = "tasks.populate"
result_expires = 30
timezone = "UTC"

accept_content = ["json", "msgpack", "yaml"]
task_serializer = "json"
result_serializer = "json"

convex_pool_tasks = {
    "populate-convex-pools": {
        "task": "tasks.populate.populate_convex_pools",
        "schedule": crontab(minute=0, hour="*/12"),
    },
    "populate-convex-pools-snapshots": {
        "task": "tasks.populate.populate_convex_pool_snapshots",
        "schedule": crontab(minute=0, hour="*/12"),
    },
    "populate-convex-revenue-snapshots": {
        "task": "tasks.populate.populate_convex_revenue_snapshots",
        "schedule": crontab(minute=0, hour="*/12"),
    },
    "populate-convex-cumulative-revenue": {
        "task": "tasks.populate.populate_convex_cumulative_revenue",
        "schedule": crontab(minute=0, hour="*/12"),
    },
}

curve_pool_tasks = {
    f"populate-curve-pools-{chain}": {
        "task": "tasks.populate.populate_curve_pools",
        "schedule": crontab(minute=0, hour="*/12"),
        "args": (chain,),
    }
    for chain in CHAINS
}

curve_pool_snapshot_tasks = {
    f"populate-curve-pool-snapshots-{chain}": {
        "task": "tasks.populate.populate_curve_pool_snapshots",
        "schedule": crontab(minute=0, hour="*/12"),
        "args": (chain,),
    }
    for chain in CHAINS
}

beat_schedule = (
    convex_pool_tasks  # | curve_pool_tasks | curve_pool_snapshot_tasks
)
