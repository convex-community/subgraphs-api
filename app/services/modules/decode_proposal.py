from web3_input_decoder import decode_function
from web3_input_decoder.utils import get_selector_to_function_type
from hexbytes import HexBytes
from flask import current_app
from main.const.abis import ABI_MAP


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
                res.append(f" ├─ Function: {fn}\n └─ Inputs: {inputs!r}\n")
            else:
                res.append(
                    f"Direct call:\n ├─ To: {target.hex()}\n ├─ Function: {fn}\n └─ Inputs: {inputs!r}"
                )
        return "\n".join(res)
    except Exception as e:
        current_app.logger.error(f"Error decoding call data: {e}")
        return data
