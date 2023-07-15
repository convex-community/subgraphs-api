from sqlalchemy import func
from web3.constants import ADDRESS_ZERO

from main import db
from main.const import MULTICALL_CONTRACTS, CHAIN_MAINNET, PUBLIC_RPCS
from main.const.abis import CRV_USD_CONTROLLER_ABI, MULTICALL2_ABI
from web3 import Web3
import time
from models.curve.crvusd import UserState, Snapshot, Market

import logging

logger = logging.getLogger(__name__)


def get_user_info(
    controller_address, collateral_price=1.0, collateral_decimals=18
):
    controller_address = Web3.to_checksum_address(controller_address)
    w3 = Web3(
        Web3.HTTPProvider(
            PUBLIC_RPCS[CHAIN_MAINNET], request_kwargs={"timeout": 60}
        )
    )
    timestamp = int((time.time() // (15 * 60)) * (15 * 60))
    controller_contract = w3.eth.contract(
        address=controller_address, abi=CRV_USD_CONTROLLER_ABI
    )
    multicall2_contract = w3.eth.contract(
        address=MULTICALL_CONTRACTS[CHAIN_MAINNET], abi=MULTICALL2_ABI
    )
    n_loans = controller_contract.functions.n_loans().call()
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
            int(result.hex()[:64], 16) * 1e-18 if result else 0
            for _, result in results
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
            Market.controller, Market.collateralPrecision, Snapshot.oraclePrice
        )
        .join(Snapshot, Market.id == Snapshot.marketId)
        .join(
            subquery,
            (Snapshot.marketId == subquery.c.marketId)
            & (Snapshot.timestamp == subquery.c.max_timestamp),
        )
        .all()
    )
    for controller, collateral_precision, price in results:
        try:
            get_user_info(
                controller,
                collateral_price=float(price),
                collateral_decimals=collateral_precision,
            )
        except Exception as e:
            logger.error(
                f"Failed to retrieve user states for {controller}: {e}"
            )
