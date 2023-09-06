from main import db
from models.curve.crvusd import Mint, Burn, DebtCeiling
from tasks.queries.graph import grt_crvusd_query

STABLECOIN_STATUS_QUERY = """
{
  mints(first: 1000) {
    id
    addr
    amount
    transactionHash
    blockNumber
    blockTimestamp
  }
  burns(first: 1000) {
    id
    addr
    amount
    transactionHash
    blockNumber
    blockTimestamp
  }
  debtCeilings(first: 1000) {
    id
    addr
    debtCeiling
    transactionHash
    blockNumber
    blockTimestamp
  }
}
"""


def update_stable_supply_data():
    data = grt_crvusd_query(STABLECOIN_STATUS_QUERY)
    for event in data["mints"]:
        mint = Mint(
            id=event["id"],
            address=event["addr"],
            amount=float(event["amount"]) * 1e-18,
            blockTimestamp=event["blockTimestamp"],
            blockNumber=event["blockNumber"],
            transactionHash=event["transactionHash"],
        )
        db.session.merge(mint)
    for event in data["burns"]:
        burn = Burn(
            id=event["id"],
            address=event["addr"],
            amount=float(event["amount"]) * 1e-18,
            blockTimestamp=event["blockTimestamp"],
            blockNumber=event["blockNumber"],
            transactionHash=event["transactionHash"],
        )
        db.session.merge(burn)
    for event in data["debtCeilings"]:
        ceiling = DebtCeiling(
            id=event["id"],
            address=event["addr"],
            amount=float(event["debtCeiling"]) * 1e-18,
            blockTimestamp=event["blockTimestamp"],
            blockNumber=event["blockNumber"],
            transactionHash=event["transactionHash"],
        )
        db.session.merge(ceiling)

    db.session.commit()
