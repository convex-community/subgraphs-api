from main import db
from models.curve.crvusd import HistoricalKeeperDebt
from tasks.queries.graph import grt_crvusd_query

DEBT_STATUS_QUERY = """
{
  pegKeepers(first: 1000) {
  id
  withdrawals(first: 1000 orderBy: blockTimestamp orderDirection: desc) {
    id
    debt
    blockTimestamp
    blockNumber
    }
  provides(first: 1000 orderBy: blockTimestamp orderDirection: desc) {
    id
    debt
    blockTimestamp
    blockNumber
    }
  }
}
"""


def update_keeper_debt_data():
    data = grt_crvusd_query(DEBT_STATUS_QUERY)
    for keeper in data["pegKeepers"]:
        keeper_id = keeper["id"]
        for event in keeper["withdrawals"] + keeper["provides"]:
            debt = HistoricalKeeperDebt(
                id=event["id"],
                keeperId=keeper_id,
                debt=event["debt"],
                timestamp=event["blockTimestamp"],
                blockNumber=event["blockNumber"],
            )
            db.session.merge(debt)

    db.session.commit()
