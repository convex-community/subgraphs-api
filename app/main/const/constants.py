from enum import Enum
import os
from main.const import (
    CHAIN_MATIC,
    CHAIN_MAINNET,
    CHAIN_ARBITRUM,
    CHAIN_FANTOM,
    CHAIN_OPTIMISM,
    CHAIN_AVALANCHE,
    CHAIN_XDAI,
    CHAIN_CELO,
    CHAIN_AURORA,
    CHAIN_HARMONY,
    CHAIN_MOONBEAM,
)

OWNERSHIP = "OWNERSHIP"
PARAMETER = "PARAMETER"

DAY = 3600 * 24
WEEK = 3600 * 24 * 7
CRVUSD_CONTRACT = "0xf939e0a03fb07f59a73314e73794be0e57ac1b4e"


class PoolType(Enum):
    STABLE_FACTORY = "STABLE_FACTORY"
    CRYPTO_FACTORY = "CRYPTO_FACTORY"
    METAPOOL_FACTORY = "METAPOOL_FACTORY"
    REGISTRY_V1 = "REGISTRY_V1"
    REGISTRY_V2 = "REGISTRY_V2"
    LENDING = "LENDING"
    CRVUSD = "CRVUSD"
    TRICRYPTO_FACTORY = "TRICRYPTO_FACTORY"


MULTICALL_CONTRACTS = {
    CHAIN_MAINNET: "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696",
    CHAIN_MATIC: "0x275617327c958bD06b5D6b871E7f491D76113dd8",
    CHAIN_ARBITRUM: "0x842eC2c7D803033Edf55E478F461FC547Bc54EB2",
    CHAIN_FANTOM: "0xD98e3dBE5950Ca8Ce5a4b59630a5652110403E5c",
    CHAIN_OPTIMISM: "0x142E2FEaC30d7fc3b61f9EE85FCCad8e560154cc",
    CHAIN_AVALANCHE: "0x8755b94F88D120AB2Cc13b1f6582329b067C760d",
    CHAIN_XDAI: "0xb5b692a88BDFc81ca69dcB1d924f59f0413A602a",
    CHAIN_CELO: "0x75F59534dd892c1f8a7B172D639FA854D529ada3",
    CHAIN_AURORA: "0x49eb1F160e167aa7bA96BdD88B6C1f2ffda5212A",
    CHAIN_HARMONY: "0x34b415f4D3B332515E66F70595ace1dcF36254c5",
    CHAIN_MOONBEAM: "0x83e3b61886770de2F64AAcaD2724ED4f08F7f36B",
}

PUBLIC_RPCS = {
    CHAIN_MAINNET: "https://eth.llamarpc.com",
    CHAIN_MATIC: "https://polygon.llamarpc.com",
    CHAIN_ARBITRUM: "https://arb1.arbitrum.io/rpc",
    CHAIN_FANTOM: "https://rpcapi.fantom.network",
    CHAIN_OPTIMISM: "https://mainnet.optimism.io",
    CHAIN_AVALANCHE: "https://rpc.ankr.com/avalanche",
    CHAIN_XDAI: "https://rpc.gnosischain.com",
    CHAIN_CELO: "https://forno.celo.org",
    CHAIN_AURORA: "https://mainnet.aurora.dev",
    CHAIN_HARMONY: "https://api.harmony.one",
    CHAIN_MOONBEAM: "https://rpc.api.moonbeam.network",
}

ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY", "")
ETHERSCAN_TOKEN = os.getenv("ETHERSCAN_TOKEN", "")
# this is used for more heavy duty/frequent queries
# the couch can use public RPCs
WEB3_ALCHEMY_PROVIDER_URL = (
    "https://eth-mainnet.g.alchemy.com/v2/" + ALCHEMY_API_KEY
)

# we keep pools in here that have been hacked or cause a problem
# to filters when subgraph is still syncing with fixes
BLACKLIST = {
    "0x06364f10b501e868329afbc005b3492902d6c763": 1680315890,
    "0x8301ae4fc9c624d1d396cbdaa1ed877821d7c511": 1690578357,  # CRV/ETH
    "0xc897b98272aa23714464ea2a0bd5180f1b8c0025": 1690578357,  # msETH
    "0xc4c319e2d4d66cca4464c0c2b32c9bd23ebe784e": 1690578357,  # alETH
    "0x9848482da3ee3076165ce6497eda906e66bb85c5": 1690578357,  # JPEGd
    "0x28b0cf1bafb707f2c6826d10caf6dd901a6540c5": 1690578357,  # zus pools
    "0x68934f60758243eafaf4d2cfed27bf8010bede3a": 1690578357,  # "
    "0xbedca4252b27cc12ed7daf393f331886f86cd3ce": 1690578357,  # "
    "0xfc636d819d1a98433402ec9dec633d864014f28c": 1690578357,  # "
    "0x35b269fe0106d3645d9780c5aad97c8eb8041c40": 1600000000,  # BSN
    # FXN
    "0xc15f285679a1ef2d25f53d4cbd0265e1d02f2a92": 1690578357,
    "0x1062fd8ed633c1f080754c19317cb3912810b5e5": 1690578357,
    "0x28ca243dc0ac075dd012fcf9375c25d18a844d96": 1690578357,
    # CBETH
    "0x6e8d2b6fb24117c675c2fabc524f28cc5d81f18a": 1690578357,
    "0x73069892f6750ccaaababadc54b6b6b36b3a057d": 1690578357,
    "0x5fae7e604fc3e24fd43a72867cebac94c65b404a": 1690578357,
}
