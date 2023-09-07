from main import db
from models.curve.crvusd import Snapshot
from tasks.queries.graph import grt_crvusd_query

MARKET_QUERY = """
{
  markets(first: 1000) {
    id
  }
}
"""

SNAPSHOT_QUERY = """{
  snapshots(where:{market: "%s"} first: 500 skip: %d orderBy: timestamp orderDirection:desc)  {
  id
  available
  }
}"""


def backfill():
    data = grt_crvusd_query(MARKET_QUERY)
    for market in data["markets"]:
        snapshots = []
        for i in range(12):
            query = SNAPSHOT_QUERY % (market["id"], (i * 500))
            snap_data = grt_crvusd_query(query)
            snap_data = snap_data["snapshots"]
            if len(snap_data) > 0:
                snapshots += snap_data
            else:
                break
        # snapshots = [{"id": snapshot["id"], "available": float(snapshot["available"])} for snapshot in snapshots]
        # db.session.bulk_update_mappings(Snapshot, snapshots)
        # db.session.commit()
        for snapshot in snapshots:
            db.session.query(Snapshot).filter(
                Snapshot.id == snapshot["id"]
            ).update({Snapshot.available: float(snapshot["available"])})
        db.session.commit()
