from main import db
from models.curve.crvusd import Market, Liquidation
from tasks.queries.graph import grt_crvusd_query

LIQUIDATION_QUERY = """
{
  markets(where:{id: "%s"}) {
    collateralPrecision
    liquidations(first: 1000 orderBy: blockTimestamp orderDirection:desc) {
      id
      liquidator {
        id
      }
      user {
        id
      }
      stablecoinReceived
      debt
      collateralReceived
      oraclePrice
      blockNumber
      blockTimestamp
      transactionHash
    }
  }
}"""


def update_liquidation_data():
    markets = [m_id[0].lower() for m_id in db.session.query(Market.id).all()]
    for market in markets:
        data = grt_crvusd_query(LIQUIDATION_QUERY % market)
        for liquidation in data["markets"][0]["liquidations"]:
            new_liq = Liquidation(
                id=liquidation["id"],
                marketId=market,
                liquidator=liquidation["liquidator"]["id"],
                user=liquidation["user"]["id"],
                collateralReceived=float(liquidation["collateralReceived"])
                / (10 ** int(data["markets"][0]["collateralPrecision"])),
                stablecoinReceived=float(liquidation["stablecoinReceived"])
                * 1e-18,
                debt=float(liquidation["debt"]) * 1e-18,
                oraclePrice=float(liquidation["oraclePrice"]) * 1e-18,
                collateralReceivedUSD=(
                    float(liquidation["collateralReceived"])
                    / (10 ** int(data["markets"][0]["collateralPrecision"]))
                )
                * (float(liquidation["oraclePrice"]) * 1e-18),
                blockNumber=int(liquidation["blockNumber"]),
                blockTimestamp=int(liquidation["blockTimestamp"]),
                transactionHash=liquidation["transactionHash"],
            )
            db.session.merge(new_liq)
    db.session.commit()
