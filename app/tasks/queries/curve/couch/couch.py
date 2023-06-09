from sqlalchemy import func
import pandas as pd
from main import db
from main.const import (
    PoolType,
    CHAIN_MAINNET,
    CHAIN_MATIC,
    MULTICALL_CONTRACTS,
    PUBLIC_RPCS,
    REGISTRIES,
    CHAINS,
    CHAIN_AVALANCHE,
    CHAIN_HARMONY,
)
from main.const.abis import CURVE_POOL_V1_ABI, MULTICALL2_ABI, REGISTRY_V1_ABI
from models.curve.pool import CurvePool
from models.curve.revenue import CouchInfo
from models.curve.snapshot import CurvePoolSnapshot
from web3 import Web3
import requests

import logging

### all credits to mo!
### https://github.com/mo-anon/curve-utilities

logger = logging.getLogger(__name__)

DL_MAPPINGS = {
    CHAIN_MAINNET: "ethereum",
    CHAIN_AVALANCHE: "avax",
    CHAIN_MATIC: "polygon",
}


def get_valid_curve_pools():
    subquery = (
        db.session.query(
            CurvePoolSnapshot.pool,
            func.max(CurvePoolSnapshot.timestamp).label("max_timestamp"),
        )
        .group_by(CurvePoolSnapshot.pool)
        .subquery()
    )
    result = (
        db.session.query(
            CurvePool.id,
            CurvePool.name,
            CurvePool.address,
            CurvePool.chain,
            CurvePool.poolType,
            CurvePool.isV2,
            CurvePool.lpToken,
            CurvePool.coins,
            CurvePool.coinNames,
            CurvePool.coinDecimals,
            CurvePoolSnapshot.tvl,
            CurvePoolSnapshot.adminFee,
            CurvePoolSnapshot.xcpProfit,
            CurvePoolSnapshot.xcpProfitA,
            CurvePoolSnapshot.virtualPrice,
            CurvePoolSnapshot.lpPriceUSD,
            CurvePoolSnapshot.volumeUSD,
        )
        .join(CurvePoolSnapshot, CurvePool.address == CurvePoolSnapshot.pool)
        .join(
            subquery,
            (CurvePoolSnapshot.pool == subquery.c.pool)
            & (CurvePoolSnapshot.timestamp == subquery.c.max_timestamp),
        )
        .all()
    )
    df = pd.DataFrame(result)
    # we filter dead pools
    return df[(df["tvl"] > 0) & (df["volumeUSD"] > 100)].drop_duplicates("id")


def get_v1_factory_cushions(df, chain):

    # util functions for multicall
    def create_v1_calls(row):
        return [(row["address"], i) for i in range(len(row["coins"]))]

    v1_pools = df[
        (
            df["poolType"].isin(
                [
                    PoolType.STABLE_FACTORY.value,
                    PoolType.METAPOOL_FACTORY.value,
                    PoolType.CRVUSD.value,
                ]
            )
        )
        & (df["chain"] == chain)
    ]
    if v1_pools.empty:
        logger.warning(f"No V1 factory pools found on {chain}")
        return None
    decimals = v1_pools["coinDecimals"].explode().tolist()
    coins = v1_pools["coins"].explode().tolist()
    v1_calls_list = v1_pools.apply(create_v1_calls, axis=1).explode().tolist()

    # gotta be chain-dependent
    w3 = Web3(
        Web3.HTTPProvider(PUBLIC_RPCS[chain], request_kwargs={"timeout": 60})
    )

    pool_contract = w3.eth.contract(
        address=Web3.to_checksum_address(v1_calls_list[0][0]),
        abi=CURVE_POOL_V1_ABI,
    )
    multicall2_address = MULTICALL_CONTRACTS[chain]
    multicall2_contract = w3.eth.contract(
        address=multicall2_address, abi=MULTICALL2_ABI
    )

    calls = [
        (
            Web3.to_checksum_address(address),
            pool_contract.functions.admin_balances(
                arg
            )._encode_transaction_data(),
        )
        for address, arg in v1_calls_list
    ]

    results = multicall2_contract.functions.aggregate(calls).call()
    return_data = results[1]
    parsed_results = [
        (
            v1_calls_list[i][0],
            coins[i],
            int(result[:32].hex(), 16) / (10 ** decimals[i]) if result else 0,
        )
        for i, result in enumerate(return_data)
    ]
    balances = pd.DataFrame(parsed_results)
    balances.columns = ["address", "coin", "balance"]
    # generate a coin list to retrieve usd prices from defi llama
    coin_list = set(
        v1_pools[["chain", "coins"]]
        .explode("coins")
        .apply(
            lambda x: (
                DL_MAPPINGS[x["chain"]]
                if x["chain"] in DL_MAPPINGS
                else x["chain"]
            )
            + ":"
            + x["coins"],
            axis=1,
        )
        .tolist()
    )
    r = requests.get(
        "https://coins.llama.fi/prices/current/" + ",".join(coin_list)
    )
    dl_prices = pd.DataFrame(r.json()["coins"]).transpose()
    dl_prices.index = dl_prices.index.map(lambda x: x.split(":")[-1])
    balances["value"] = (
        balances["coin"].map(dl_prices["price"]) * balances["balance"]
    ).fillna(0)
    vals = (
        balances.groupby("address")
        .agg({"balance": lambda x: list(x), "value": lambda x: list(x)})
        .reset_index()
    )
    final_df = v1_pools.merge(vals, on="address", how="inner")
    return final_df[
        ["name", "address", "chain", "coinNames", "balance", "value"]
    ]


def get_v2_cushions(df):
    def calc_profit(row):
        xcp_profit = row["xcpProfit"]
        xcp_profit_a = row["xcpProfitA"]
        if xcp_profit > xcp_profit_a:
            fees = (xcp_profit - xcp_profit_a) * row["adminFee"] / (2)
            if fees > 0:
                return [fees * 1e-18, fees * 1e-18 * row["lpPriceUSD"]]
        return [0, 0]

    v2_pools = df[df["isV2"]].copy()
    v2_pools["xcpProfit"] = v2_pools["xcpProfit"].astype(float).fillna(0)
    v2_pools["xcpProfitA"] = v2_pools["xcpProfitA"].astype(float).fillna(0)
    v2_pools[["balance", "value"]] = (
        v2_pools.apply(calc_profit, axis=1)
        .apply(pd.Series)
        .applymap(lambda x: [x])
    )
    v2_pools["coinNames"] = "LP token"
    return v2_pools[
        ["name", "address", "chain", "coinNames", "balance", "value"]
    ]


def get_v1_registry_cushions(df, chain):
    registry_pools = df[
        (
            df["poolType"].isin(
                [PoolType.REGISTRY_V1.value, PoolType.LENDING.value]
            )
        )
        & (df["chain"] == chain)
        & (~df["isV2"])
    ]
    w3 = Web3(
        Web3.HTTPProvider(PUBLIC_RPCS[chain], request_kwargs={"timeout": 60})
    )

    if registry_pools.empty:
        logger.warning(f"No V1 registry pools found on {chain}")
        return None
    registry = Web3.to_checksum_address(REGISTRIES[chain])
    registry_contract = w3.eth.contract(address=registry, abi=REGISTRY_V1_ABI)
    multicall2_address = MULTICALL_CONTRACTS[chain]
    multicall2_contract = w3.eth.contract(
        address=multicall2_address, abi=MULTICALL2_ABI
    )
    calls = [
        (
            registry,
            registry_contract.functions.get_admin_balances(
                Web3.to_checksum_address(pool)
            )._encode_transaction_data(),
        )
        for pool in registry_pools["address"]
    ]
    decimals = registry_pools["coinDecimals"].tolist()
    balances = (
        registry_pools[["address", "coins"]]
        .explode("coins")
        .reset_index(drop=True)
    )

    try:
        results = multicall2_contract.functions.tryAggregate(
            False, calls
        ).call()
        parsed_results = [
            [0] * len(decimals[index])
            if not success
            else [
                int(calldata[i * 32 : (i + 1) * 32].hex(), 16)
                / (10 ** decimals[index][i])
                for i in range(len(decimals[index]))
            ]
            for index, (success, calldata) in enumerate(results)
        ]
    except Exception as e:
        logger.warning(f"Multicall v2 likely not supported on {chain}: {e}")
        # not all chain support multicall2
        results = multicall2_contract.functions.aggregate(calls).call()
        parsed_results = [
            [
                int(calldata[i * 32 : (i + 1) * 32].hex(), 16)
                / (10 ** decimals[index][i])
                for i in range(len(decimals[index]))
            ]
            for index, calldata in enumerate(results[1])
        ]

    balances["balance"] = (
        pd.Series(parsed_results).explode().reset_index(drop=True)
    )
    coin_list = set(
        registry_pools[["chain", "coins"]]
        .explode("coins")
        .apply(
            lambda x: (
                DL_MAPPINGS[x["chain"]]
                if x["chain"] in DL_MAPPINGS
                else x["chain"]
            )
            + ":"
            + x["coins"],
            axis=1,
        )
        .tolist()
    )
    r = requests.get(
        "https://coins.llama.fi/prices/current/" + ",".join(coin_list)
    )
    dl_prices = pd.DataFrame(r.json()["coins"]).transpose()
    dl_prices.index = dl_prices.index.map(lambda x: x.split(":")[-1])
    balances["value"] = (
        balances["coins"].map(dl_prices["price"]) * balances["balance"]
    ).fillna(0)
    vals = (
        balances.groupby("address")
        .agg({"balance": lambda x: list(x), "value": lambda x: list(x)})
        .reset_index()
    )
    final_df = registry_pools.merge(vals, on="address", how="inner")
    return final_df[
        ["name", "address", "chain", "coinNames", "balance", "value"]
    ]


def get_v1(df):
    res = []
    for chain in CHAINS:
        # no multicall on harmony
        if chain == CHAIN_HARMONY:
            continue
        try:
            v1_factory = get_v1_factory_cushions(df, chain)
            if v1_factory is not None:
                res.append(v1_factory)
        except Exception as e:
            logger.error(
                f"Error parsing fees for factory v1 pools on chain {chain}: {e}"
            )

        try:
            v1_registry = get_v1_registry_cushions(df, chain)
            if v1_registry is not None:
                res.append(v1_registry)
        except Exception as e:
            logger.error(
                f"Error parsing fees for registry v1 pools on chain {chain}: {e}"
            )
    return res


def check_cushions():
    df = get_valid_curve_pools()

    res = get_v1(df)

    try:
        v2_pools = get_v2_cushions(df)
        if v2_pools is not None:
            res.append(v2_pools)

    except Exception as e:
        logger.error(f"Error parsing fees for v2 pools: {e}")

    total = pd.concat(res, axis=0).reset_index(drop=True)
    total["totalUSD"] = total["value"].apply(sum)

    for entry in total.to_dict(orient="records"):
        new_cushion = CouchInfo(
            id=entry["address"] + "-" + entry["chain"],
            poolId=entry["address"] + "-" + entry["chain"],
            balance=entry["balance"],
            value=entry["value"],
            totalUSD=entry["totalUSD"],
        )

        db.session.merge(new_cushion)
    db.session.commit()
