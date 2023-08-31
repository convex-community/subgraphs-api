from sqlalchemy import func

from main import db
from models.curve.crvusd import UserStateSnapshot, Market, MarketLosers
import pandas as pd


def get_loser_proportions():
    subquery = (
        db.session.query(
            UserStateSnapshot.marketId,
            func.max(UserStateSnapshot.timestamp).label("max_timestamp"),
        )
        .group_by(UserStateSnapshot.marketId)
        .subquery()
    )

    results = (
        db.session.query(UserStateSnapshot, Market.collateralName)
        .join(Market, Market.id == UserStateSnapshot.marketId)
        .join(
            subquery,
            (UserStateSnapshot.marketId == subquery.c.marketId)
            & (UserStateSnapshot.timestamp == subquery.c.max_timestamp),
        )
        .all()
    )
    df = pd.DataFrame(
        [
            (
                r.UserStateSnapshot.marketId,
                r.UserStateSnapshot.loss > 0,
                r.collateralName,
            )
            for r in results
        ],
        columns=["market", "has_loss", "collateralName"],
    )
    import logging

    logging.warning(df)
    if df.empty:
        return []
    df_pivot = (
        df.groupby(["market", "collateralName", "has_loss"])
        .size()
        .unstack(fill_value=0)
    )

    df_pivot["proportion"] = (
        df_pivot[True] / (df_pivot[True] + df_pivot[False]) * 100
    )

    return [
        MarketLosers(
            market=index[0], marketName=index[1], losers=row["proportion"]
        )
        for index, row in df_pivot.iterrows()
    ]
