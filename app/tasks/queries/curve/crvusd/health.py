from sqlalchemy import func
from web3.constants import ADDRESS_ZERO

from main import db
from main.const import MULTICALL_CONTRACTS, CHAIN_MAINNET, PUBLIC_RPCS
from main.const.abis import (
    CRV_USD_CONTROLLER_ABI,
    MULTICALL2_ABI,
    CRV_USD_LLAMMA_ABI,
)
from web3 import Web3
import time
from models.curve.crvusd import UserState, Snapshot, Market, Amm

import logging

logger = logging.getLogger(__name__)


def decode_int256(data):
    int_max = 2**255 - 1
    value = int(data, 16)
    if value > int_max:
        value -= 2**256
    return value


def get_user_info(
    controller_address, llamma, collateral_price=1.0, collateral_decimals=18
):
    controller_address = Web3.to_checksum_address(controller_address)
    llamma_address = Web3.to_checksum_address(llamma)
    w3 = Web3(
        Web3.HTTPProvider(
            PUBLIC_RPCS[CHAIN_MAINNET], request_kwargs={"timeout": 60}
        )
    )
    timestamp = int((time.time() // (15 * 60)) * (15 * 60))
    controller_contract = w3.eth.contract(
        address=controller_address, abi=CRV_USD_CONTROLLER_ABI
    )
    llamma_contract = w3.eth.contract(
        address=llamma_address, abi=CRV_USD_LLAMMA_ABI
    )
    multicall2_contract = w3.eth.contract(
        address=MULTICALL_CONTRACTS[CHAIN_MAINNET], abi=MULTICALL2_ABI
    )
    n_loans = controller_contract.functions.n_loans().call()
    active_band = llamma_contract.functions.active_band().call()
    for i in range(0, n_loans, 1000):
        logger.info(f"Fetching user addresses {i}:{i+1000}")
        calls = [
            (
                controller_address,
                controller_contract.functions.loans(
                    i
                )._encode_transaction_data(),
            )
            for i in range(i, min(n_loans, i + 1000))
        ]
        results = multicall2_contract.functions.tryAggregate(
            False, calls
        ).call()
        user_addresses = [
            Web3.to_checksum_address("0x" + result.hex()[24:])
            if result
            else ADDRESS_ZERO
            for _, result in results
        ]
        logger.info("Fetching user_states")
        calls = [
            (
                controller_address,
                controller_contract.functions.user_state(
                    user
                )._encode_transaction_data(),
            )
            for user in user_addresses
        ]
        results = multicall2_contract.functions.tryAggregate(
            False, calls
        ).call()
        decimals = [collateral_decimals, 18, 18, 0]
        user_states = [
            [
                int(calldata[i * 32 : (i + 1) * 32].hex(), 16)
                / (10 ** decimals[i])
                for i in range(len(decimals))
            ]
            for _, calldata in results
        ]
        logger.info("Fetching user health")
        calls = [
            (
                controller_address,
                controller_contract.functions.health(
                    user
                )._encode_transaction_data(),
            )
            for user in user_addresses
        ]
        results = multicall2_contract.functions.tryAggregate(
            False, calls
        ).call()
        user_health = [
            decode_int256(result.hex()[:64]) * 1e-18 if result else 0
            for _, result in results
        ]
        logger.info("Fetching user band range")
        calls = [
            (
                llamma_address,
                llamma_contract.functions.read_user_tick_numbers(
                    user
                )._encode_transaction_data(),
            )
            for user in user_addresses
        ]
        results = multicall2_contract.functions.tryAggregate(
            False, calls
        ).call()
        user_bands = [
            [
                decode_int256(calldata[i * 32 : (i + 1) * 32].hex())
                for i in range(2)
            ]
            for _, calldata in results
        ]

        for j, user in enumerate(user_addresses):
            new_state = UserState(
                id=controller_address.lower()
                + "-"
                + user
                + "-"
                + str(timestamp),
                marketId=controller_address.lower(),
                index=i + j,
                user=user,
                collateral=user_states[j][0],
                collateralUsd=user_states[j][0] * collateral_price,
                stableCoin=user_states[j][1],
                debt=user_states[j][2],
                N=user_states[j][3],
                N1=user_bands[j][0],
                N2=user_bands[j][1],
                softLiq=user_bands[j][0] <= active_band,
                health=user_health[j],
                timestamp=timestamp,
            )
            db.session.merge(new_state)
    db.session.commit()


def update_user_states_and_health():
    subquery = (
        db.session.query(
            Snapshot.marketId,
            func.max(Snapshot.timestamp).label("max_timestamp"),
        )
        .group_by(Snapshot.marketId)
        .subquery()
    )
    results = (
        db.session.query(
            Market.controller,
            Market.collateralPrecision,
            Snapshot.oraclePrice,
            Amm.id,
        )
        .join(Snapshot, Market.id == Snapshot.marketId)
        .join(Amm, Market.amm == Amm.id)
        .join(
            subquery,
            (Snapshot.marketId == subquery.c.marketId)
            & (Snapshot.timestamp == subquery.c.max_timestamp),
        )
        .all()
    )
    for controller, collateral_precision, price, amm_id in results:
        try:
            get_user_info(
                controller,
                llamma=amm_id,
                collateral_price=float(price),
                collateral_decimals=collateral_precision,
            )
        except Exception as e:
            logger.error(
                f"Failed to retrieve user states for {controller}: {e}"
            )
