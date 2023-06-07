from main import db
from models.curve.crvusd import (
    Market,
    Amm,
    MonetaryPolicy,
    PegKeeper,
    DebtFraction,
    VolumeSnapshot,
    Snapshot,
)
from tasks.queries.graph import grt_crvusd_query

MARKET_QUERY = """
{
  markets(first: 1000) {
    id
    collateral
    collateralPrecision
    collateralName
    controller
    index
    amm {
      id
      coins
      coinNames
      coinDecimals
      basePrice
      totalSwapVolume
      totalVolume
      totalDepositVolume
      volumeSnapshots(first: 1000 orderBy: timestamp orderDirection:desc) {
        id
        swapVolumeUSD
        depositVolumeUSD
        totalVolumeUSD
        count
        timestamp
      }
    }
    monetaryPolicy {
      id
      pegKeepers(first: 1000) {
        id
        active
        debt
        totalProfit
        totalProvided
        totalWithdrawn
      }
    debtFractions(first: 100 orderBy: blockTimestamp orderDirection: desc) {
      id
      target
      blockNumber
      blockTimestamp
      transactionHash
    }
    }
  }
}
"""

SNAPSHOT_QUERY = """{
  snapshots(where:{market: "%s"} first: 1000 orderBy: timestamp orderDirection:desc)  {
  id
  A
  rate
  futureRate
  liquidationDiscount
  loanDiscount

  minted
  redeemed
  totalKeeperDebt
  totalCollateral
  totalCollateralUsd
  totalSupply
  totalStableCoin

  totalDebt
  nLoans

  crvUsdAdminFees
  collateralAdminFees
  fee
  adminFee

  ammPrice
  oraclePrice
  basePrice

  activeBand
  minBand
  maxBand

  blockNumber
  timestamp
  }
}"""


def update_crvusd_market_data():
    data = grt_crvusd_query(MARKET_QUERY)
    for market in data["markets"]:
        new_market = Market(
            id=market["id"],
            collateral=market["collateral"],
            collateralName=market["collateralName"],
            collateralPrecision=market["collateralPrecision"],
            controller=market["controller"],
            amm=market["amm"]["id"],
            monetaryPolicy=market["monetaryPolicy"]["id"],
            index=market["index"],
        )

        amm = market["amm"]
        new_amm = Amm(
            id=amm["id"],
            market=market["id"],
            coins=amm["coins"],
            coinNames=amm["coinNames"],
            basePrice=amm["basePrice"],
            totalSwapVolume=amm["totalSwapVolume"],
            totalDepositVolume=amm["totalDepositVolume"],
            totalVolume=amm["totalVolume"],
        )

        new_policy = MonetaryPolicy(
            id=market["monetaryPolicy"]["id"], market=market["id"]
        )
        db.session.merge(new_amm)
        db.session.merge(new_policy)
        db.session.merge(new_market)

        for keeper in market["monetaryPolicy"]["pegKeepers"]:
            new_keeper = PegKeeper(
                id=keeper["id"],
                policy=new_policy,
                active=keeper["active"],
                debt=keeper["debt"],
                totalProvided=keeper["totalProvided"],
                totalWithdrawn=keeper["totalWithdrawn"],
                totalProfit=keeper["totalProfit"],
            )
            db.session.merge(new_keeper)

        for fraction in market["monetaryPolicy"]["debtFractions"]:
            new_fraction = DebtFraction(
                id=fraction["id"],
                policy=new_policy,
                target=fraction["target"],
                blockNumber=fraction["blockNumber"],
                blockTimestamp=fraction["blockTimestamp"],
                transactionHash=fraction["transactionHash"],
            )
            db.session.merge(new_fraction)

        for vol_snapshot in market["amm"]["volumeSnapshots"]:
            new_vol_snapshot = VolumeSnapshot(
                id=vol_snapshot["id"],
                amm=new_amm,
                swapVolumeUsd=vol_snapshot["swapVolumeUSD"],
                depositVolumeUsd=vol_snapshot["depositVolumeUSD"],
                totalVolumeUsd=vol_snapshot["totalVolumeUSD"],
                count=vol_snapshot["count"],
                timestamp=vol_snapshot["timestamp"],
            )
            db.session.merge(new_vol_snapshot)
        db.session.commit()

        snapshots = get_market_snapshots(market["id"])["snapshots"]
        for snapshot in snapshots:
            new_snapshot = Snapshot(
                id=snapshot["id"],
                market=new_market,
                llamma=new_amm,
                policy=new_policy,
                A=snapshot["A"],
                rate=snapshot["rate"],
                futureRate=snapshot["futureRate"],
                liquidationDiscount=snapshot["liquidationDiscount"],
                loanDiscount=snapshot["loanDiscount"],
                minted=snapshot["minted"],
                redeemed=snapshot["redeemed"],
                totalKeeperDebt=snapshot["totalKeeperDebt"],
                totalCollateral=snapshot["totalCollateral"],
                totalCollateralUsd=snapshot["totalCollateralUsd"],
                totalSupply=snapshot["totalSupply"],
                totalStableCoin=snapshot["totalStableCoin"],
                totalDebt=snapshot["totalDebt"],
                nLoans=snapshot["nLoans"],
                crvUsdAdminFees=snapshot["crvUsdAdminFees"],
                collateralAdminFees=snapshot["collateralAdminFees"],
                fee=snapshot["fee"],
                adminFee=snapshot["adminFee"],
                ammPrice=snapshot["ammPrice"],
                oraclePrice=snapshot["oraclePrice"],
                basePrice=snapshot["basePrice"],
                activeBand=snapshot["activeBand"],
                minBand=snapshot["minBand"],
                maxBand=snapshot["maxBand"],
                blockNumber=snapshot["blockNumber"],
                timestamp=snapshot["timestamp"],
            )
            db.session.merge(new_snapshot)
        db.session.commit()


def get_market_snapshots(market):
    query = SNAPSHOT_QUERY % market
    return grt_crvusd_query(query)
