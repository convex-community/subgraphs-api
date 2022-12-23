from typing import List

import numpy as np

from itertools import combinations

from web3 import Web3, HTTPProvider

from main.const import (
    CHAIN_MAINNET,
    CHAIN_MATIC,
    CHAIN_ARBITRUM,
    CHAIN_OPTIMISM,
)
from main.const.abis import CRYPTO_SWAP_ABI
from models.curve.bonding import CurvePoolBondingCurve
from services.curve import get_pool_snapshots, get_pool_metadata
from services.modules.stableswap import get_stable_d, get_stable_y


def get_v1_curve(
    A: int, xp: List[int], coins: List[str], resolution: int
) -> List[CurvePoolBondingCurve]:
    res = []
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


# temp fix until gamma values are stored on subgraph
def get_gamma(pool: str, chain: str) -> int:
    endpoint_map = {
        CHAIN_MAINNET: "https://eth-mainnet.g.alchemy.com/v2/fRfkh05hxMr1ruv1A9ptgDxk1UDEBoGP",
        CHAIN_MATIC: "https://polygon-mainnet.g.alchemy.com/v2/bUZ6f1AjZt6Ex6-IUDUdX88ASVRmOz13",
        CHAIN_ARBITRUM: "https://arb-mainnet.g.alchemy.com/v2/m4sG_ELr8JLm7TCSHXAICm6SwrCpaxsh",
        CHAIN_OPTIMISM: "https://opt-mainnet.g.alchemy.com/v2/zcqeE7qSHKUNH7X4DKnk8Pn3lO6fgxmH",
    }
    if chain not in endpoint_map:
        return 145000000000000  # yolo
    web3 = Web3(HTTPProvider(endpoint_map[chain]))
    contract = web3.eth.contract(pool, abi=CRYPTO_SWAP_ABI)
    return contract.functions.gamma().call()


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
