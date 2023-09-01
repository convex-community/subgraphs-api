from main import db
from models.curve.crvusd import UserStateSnapshot
from tasks.queries.graph import grt_crvusd_query


USER_STATE_QUERY = """{
  users(first: 500 skip: %d orderBy: firstActionBlock orderDirection:desc){
    id
    stateSnapshots(first: 1000 orderBy: timestamp orderDirection: desc) {
      id
      market {
        id
        collateralName
      }
      snapshot {
        activeBand
        oraclePrice
      }
      collateral
      stablecoin
      collateralUp
      depositedCollateral
      n
      n1
      n2
      loss
      lossPct
      health
      debt
      timestamp
    }
  }
}"""


def update_user_states():
    users = []
    for i in range(12):
        query = USER_STATE_QUERY % (i * 500)
        data = grt_crvusd_query(query)
        data = data["users"]
        if len(data) > 0:
            users += data
        else:
            break

    for user in users:
        for snapshot in user["stateSnapshots"]:
            entry = UserStateSnapshot(
                id=snapshot["id"],
                user=user["id"],
                marketId=snapshot["market"]["id"],
                collateral=float(snapshot["collateral"]),
                stablecoin=float(snapshot["stablecoin"]),
                collateralUsd=float(snapshot["collateral"])
                * float(snapshot["snapshot"]["oraclePrice"]),
                oraclePrice=float(snapshot["snapshot"]["oraclePrice"]),
                collateralUp=float(snapshot["collateralUp"]),
                depositedCollateral=float(snapshot["depositedCollateral"]),
                activeBand=int(snapshot["snapshot"]["activeBand"]),
                n=int(snapshot["n"]),
                n1=int(snapshot["n1"]),
                n2=int(snapshot["n2"]),
                softLiq=int(snapshot["n1"])
                <= int(snapshot["snapshot"]["activeBand"]),
                loss=float(snapshot["loss"]),
                lossPct=float(snapshot["lossPct"]),
                health=float(snapshot["health"]),
                debt=float(snapshot["debt"]),
                timestamp=int(snapshot["timestamp"]),
            )
            db.session.merge(entry)
    db.session.commit()
