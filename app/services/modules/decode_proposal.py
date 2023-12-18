from typing import Optional
from web3 import Web3
from web3_input_decoder import decode_function
from web3_input_decoder.utils import get_selector_to_function_type
from hexbytes import HexBytes
from flask import current_app

from main.const.constants import ETHERSCAN_TOKEN
from main.const.abis import ABI_MAP
import json
import time
import requests


def get_abi(pool_address: str) -> Optional[list[dict]]:
    if pool_address in ABI_MAP:
        return ABI_MAP[pool_address]
    for i in range(3):
        url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={pool_address}&apikey={ETHERSCAN_TOKEN}"
        abi_response = requests.get(url).json()
        if abi_response["status"] == "1":
            return json.loads(abi_response["result"])
        else:
            time.sleep(5)
    return None


def format_inputs(inputs):
    res = []
    for arg in inputs:
        if arg[0] == "address":
            res.append((arg[0], arg[1], Web3.to_checksum_address(arg[2])))
        else:
            res.append(arg)
    return res


def convert_bytes_to_hex(item):
    if isinstance(item, bytes):
        return item.hex()
    elif isinstance(item, tuple):
        return tuple(convert_bytes_to_hex(sub_item) for sub_item in item)
    else:
        return item


# TODO: decoding routing needs a thorough clean up
def parse_data(data: str) -> str:
    try:
        script = HexBytes(data)
        res = []
        idx = 4
        while idx < len(script):
            target = script[idx : idx + 20]
            if target.hex() not in ABI_MAP:
                res.append(
                    f"Failed to fully decode data for call to {target.hex()}: {script[idx:].hex()}"
                )
                break
            abi = ABI_MAP[target.hex()]
            idx += 20
            length = int(script[idx : idx + 4].hex(), 16)
            idx += 4
            calldata = script[idx : idx + length]
            idx += length
            fn = get_selector_to_function_type(abi).get(calldata[:4])["name"]  # type: ignore
            inputs = decode_function(abi, calldata)
            if calldata[:4].hex() == "0xb61d27f6":
                agent_target = inputs[0][-1]
                res.append(
                    f"Call via agent ({target.hex()}):\n ├─ To: {agent_target}"
                )
                if agent_target not in ABI_MAP:
                    res.append(
                        f"Failed to fully decode data for call to {agent_target}: {inputs[2][-1].hex()}"
                    )
                    continue
                abi = ABI_MAP[agent_target]
                print(inputs[2][-1][:4].hex())
                try:
                    fn = get_selector_to_function_type(abi).get(  # type: ignore
                        inputs[2][-1][:4]
                    )[
                        "name"
                    ]
                except TypeError:
                    res.append(
                        f"Failed to fully decode data for call to {agent_target}: {inputs[2][-1].hex()}"
                    )
                    continue

                inputs = decode_function(abi, inputs[2][-1])
                formatted_inputs = [
                    convert_bytes_to_hex(tup) for tup in inputs
                ]
                res.append(
                    f" ├─ Function: {fn}\n └─ Inputs: {formatted_inputs!r}\n"
                )
            else:
                res.append(
                    f"Direct call:\n ├─ To: {target.hex()}\n ├─ Function: {fn}\n └─ Inputs: {inputs!r}"
                )
        return "\n".join(res)
    except Exception as e:
        current_app.logger.error(f"Error decoding call data: {e}")
        return data


def parse_data_etherscan(data: str) -> str:
    try:
        script = HexBytes(data)
        res = []
        idx = 4
        while idx < len(script):
            target = script[idx : idx + 20]
            abi = get_abi(target.hex())
            if not abi:
                res.append(
                    f"Failed to fully decode data for call to {Web3.to_checksum_address(target.hex())}: {script[idx:].hex()}"
                )
                break
            idx += 20
            length = int(script[idx : idx + 4].hex(), 16)
            idx += 4
            calldata = script[idx : idx + length]
            idx += length
            fn = get_selector_to_function_type(abi).get(calldata[:4])["name"]  # type: ignore
            inputs = format_inputs(decode_function(abi, calldata))
            if calldata[:4].hex() == "0xb61d27f6":
                agent_target = inputs[0][-1]
                res.append(
                    f"Call via agent ({Web3.to_checksum_address(target.hex())}):\n ├─ To: {Web3.to_checksum_address(agent_target)}"
                )
                abi = get_abi(agent_target)
                if not abi:
                    res.append(
                        f"Failed to fully decode data for call to {agent_target}: {inputs[2][-1].hex()}"
                    )
                    continue
                try:
                    fn = get_selector_to_function_type(abi).get(  # type: ignore
                        inputs[2][-1][:4]
                    )[
                        "name"
                    ]
                except TypeError:
                    res.append(
                        f"Failed to fully decode data for call to {Web3.to_checksum_address(agent_target)}: {inputs[2][-1].hex()}"
                    )
                    continue
                inputs = format_inputs(decode_function(abi, inputs[2][-1]))
                formatted_inputs = [
                    convert_bytes_to_hex(tup) for tup in inputs
                ]
                res.append(
                    f" ├─ Function: {fn}\n └─ Inputs: {formatted_inputs!r}\n"
                )
            else:
                res.append(
                    f"Direct call:\n ├─ To: {Web3.to_checksum_address(target.hex())}\n ├─ Function: {fn}\n └─ Inputs: {inputs!r}"
                )
        return "\n".join(res)
    except Exception as e:
        current_app.logger.error(f"Error decoding call data: {e}")
        return data
