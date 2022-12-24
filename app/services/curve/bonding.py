from typing import List

import numpy as np

from itertools import combinations

from gmpy2 import mpz

from models.curve.bonding import CurvePoolBondingCurve
from services.curve import get_pool_snapshots, get_pool_metadata
from services.modules.cryptoswap import get_crypto_d, get_crypto_y
from services.modules.stableswap import get_stable_d, get_stable_y


def get_v1_curve(
    A: int, xp: List[str], coins: List[str], resolution: int
) -> List[CurvePoolBondingCurve]:
    res = []
    xp = [mpz(x) for x in xp]
    D = get_stable_d(xp, A)
    xp = [D // len(xp) for _ in xp]
    truncate = 0.0005
    combos = list(combinations(range(len(coins)), 2))
    for combo in combos:
        i, j = combo
        xs_n = np.linspace(
            int(D * truncate),
            get_stable_y(A, j, i, int(D * truncate), xp),
            resolution,
        ).round()
        ys_n = []
        for x in xs_n:
            ys_n.append(get_stable_y(A, i, j, int(x), xp))
        res.append(
            CurvePoolBondingCurve(
                coin0=coins[i], coin1=coins[j], x=xs_n, y=ys_n
            )
        )
    return res


def get_v2_curve(
    A: int, gamma: int, xp: List[str], coins: List[str], resolution: int
) -> List[CurvePoolBondingCurve]:
    """

    :param A: Amplification param
    :param gamma: gamma
    :param xp: Normalized to units of D!
    :param coins: list of coin names
    :param resolution: data points to return
    :return: bounding curve for each coin pair
    """
    res = []
    xp = [mpz(x) for x in xp]
    D = get_crypto_d(A, gamma, xp)
    truncate = 0.1
    combos = list(combinations(range(len(coins)), 2))
    for combo in combos:
        i, j = combo
        xn = np.linspace(
            int(D * truncate), int(D * (1 / truncate)), resolution
        )
        xpi = [D // len(xp) for _ in xp]
        xpi[i] = 0
        xrange = []
        for x in xn:
            xpi[j] = x
            xrange.append(get_crypto_y(A, gamma, xpi, D, i))

        xpj = [D // len(xp) for _ in xp]
        xpj[j] = 0
        yrange = []
        for x in xrange:
            xpj[i] = x
            yrange.append(get_crypto_y(A, gamma, xpj, D, j))

        res.append(
            CurvePoolBondingCurve(
                coin0=coins[i], coin1=coins[j], x=xrange, y=yrange
            )
        )
    return res


# temp fix until gamma values are stored on subgraph
def get_gamma(pool: str, chain: str) -> int:
    return 145000000000000


def get_bonding_curves(
    chain: str, pool: str, resolution: int = 1000
) -> List[CurvePoolBondingCurve]:
    latest_snapshot = next(
        iter(get_pool_snapshots(chain, pool, limit=1)), None
    )
    pool_metadata = next(iter(get_pool_metadata(chain, pool)), None)

    if latest_snapshot and pool_metadata:
        A = latest_snapshot.A
        normalized_reserves = latest_snapshot.normalizedReserves
        coins = pool_metadata.coinNames
        if pool_metadata.isV2:
            gamma = get_gamma(pool, chain)
            gamma += 1
            return []
        else:
            return get_v1_curve(A, normalized_reserves, coins, resolution)
    return []
