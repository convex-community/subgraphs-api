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

ranking_tasks = {
    "rankings-daily": {
        "task": "tasks.populate.populate_daily_rankings",
        "schedule": crontab(minute=0, hour="*/12"),
    },
    "rankings-hourly": {
        "task": "tasks.populate.populate_hourly_rankings",
        "schedule": crontab(minute="*/10"),
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

curve_couch_tasks = {
    "populate-couch-info": {
        "task": "tasks.populate.populate_couch_info",
        "schedule": crontab(minute="*/60"),
    },
}

curve_pool_snapshot_tasks = {
    f"populate-curve-pool-snapshots-{chain}": {
        "task": "tasks.populate.populate_curve_pool_snapshots",
        "schedule": crontab(minute=0, hour="*/12"),
        "args": (chain,),
    }
    for chain in CHAINS
}

crvusd_tasks = {
    "populate-crvusd-prices": {
        "task": "tasks.populate.populate_crvusd_prices",
        "schedule": crontab(minute="*/60"),
    },
    "populate-crvusd-market-data": {
        "task": "tasks.populate.populate_crvusd_market_data",
        "schedule": crontab(minute="*/60"),
    },
}

beat_schedule = (
    convex_pool_tasks
    | curve_pool_tasks
    | curve_couch_tasks
    | curve_pool_snapshot_tasks
    | ranking_tasks
    | crvusd_tasks
)
