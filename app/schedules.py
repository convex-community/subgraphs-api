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

curve_revenue_tasks = {
    "populate-revenue-breakdown": {
        "task": "tasks.populate.populate_revenue_breakdown",
        "schedule": crontab(hour="*/12"),
    },
    "populate-protocol-revenue": {
        "task": "tasks.populate.populate_protocol_revenue",
        "schedule": crontab(hour="*/12"),
    },
}

curve_dao_tasks = {
    "populate-dao-proposals-info": {
        "task": "tasks.populate.populate_dao_decoded_proposal_data",
        "schedule": crontab(minute="*/2"),
    },
}

curve_pool_snapshot_tasks = {
    f"populate-curve-pool-snapshots-{chain}": {
        "task": "tasks.populate.populate_curve_pool_snapshots",
        "schedule": crontab(minute="*/12"),
        "args": (chain,),
    }
    for chain in CHAINS
}

crvusd_tasks = {
    "populate-crvusd-prices": {
        "task": "tasks.populate.populate_crvusd_prices",
        "schedule": crontab(minute="*/60"),
    },
    "populate-crvusd-historical-debt": {
        "task": "tasks.populate.populate_crvusd_keeper_debt_data",
        "schedule": crontab(minute=0, hour="*/4"),
    },
    "populate-crvusd-market-data": {
        "task": "tasks.populate.populate_crvusd_market_data",
        "schedule": crontab(minute="*/60"),
    },
    "populate-crvusd-user_state_snapshots": {
        "task": "tasks.populate.populate_user_state_snapshots",
        "schedule": crontab(minute="*/120"),
    },
    "populate-crvusd-user_states": {
        "task": "tasks.populate.populate_user_states",
        "schedule": crontab(minute="*/15"),
    },
    "populate-crvusd-liquidation_data": {
        "task": "tasks.populate.populate_liquidations",
        "schedule": crontab(minute="*/15"),
    },
    "populate-crvusd-stable_supply_data": {
        "task": "tasks.populate.populate_supply_events",
        "schedule": crontab(minute="*/15"),
    },
}

backfill = {
    "populate-backfill": {
        "task": "tasks.populate.populate_backfill",
        "schedule": crontab(minute="*/5"),
    },
}

beat_schedule = (
    convex_pool_tasks
    | curve_pool_tasks
    | curve_couch_tasks
    | curve_pool_snapshot_tasks
    | ranking_tasks
    | crvusd_tasks
    | curve_dao_tasks
    | curve_revenue_tasks
)
