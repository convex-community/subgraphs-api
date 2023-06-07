import os

CHAIN_MAINNET = "mainnet"
CHAIN_ARBITRUM = "arbitrum"
CHAIN_AVALANCHE = "avalanche"
CHAIN_FANTOM = "fantom"
CHAIN_HARMONY = "harmony"
CHAIN_MATIC = "matic"
CHAIN_MOONBEAM = "moonbeam"
CHAIN_OPTIMISM = "optimism"
CHAIN_XDAI = "xdai"
CHAIN_CELO = "celo"
CHAIN_AURORA = "aurora"

SUBGRAPHS_API_KEY = os.getenv("GRAPH_API_KEY")

CHAINS = [
    CHAIN_MAINNET,
    CHAIN_ARBITRUM,
    CHAIN_AVALANCHE,
    CHAIN_FANTOM,
    CHAIN_HARMONY,
    CHAIN_MATIC,
    CHAIN_MOONBEAM,
    CHAIN_OPTIMISM,
    CHAIN_XDAI,
    CHAIN_CELO,
    CHAIN_AURORA,
]

SUBGRAPH_MAINNET_API_PROD = (
    "https://api.thegraph.com/subgraphs/name/convex-community/volume-mainnet"
)
SUBGRAPH_ARBITRUM_API_PROD = (
    "https://api.thegraph.com/subgraphs/name/convex-community/volume-arbitrum"
)
SUBGRAPH_AVALANCHE_API_PROD = (
    "https://api.thegraph.com/subgraphs/name/convex-community/volume-avalanche"
)
SUBGRAPH_FANTOM_API_PROD = (
    "https://api.thegraph.com/subgraphs/name/convex-community/volume-fantom"
)
SUBGRAPH_HARMONY_API_PROD = (
    "https://api.thegraph.com/subgraphs/name/convex-community/volume-harmony"
)
SUBGRAPH_MATIC_API_PROD = (
    "https://api.thegraph.com/subgraphs/name/convex-community/volume-matic"
)
SUBGRAPH_MOONBEAM_API_PROD = (
    "https://api.thegraph.com/subgraphs/name/convex-community/volume-moonbeam"
)
SUBGRAPH_OPTIMISM_API_PROD = (
    "https://api.thegraph.com/subgraphs/name/convex-community/volume-optimism"
)
SUBGRAPH_XDAI_API_PROD = (
    "https://api.thegraph.com/subgraphs/name/convex-community/volume-xdai"
)
SUBGRAPH_CELO_API_PROD = (
    "https://api.thegraph.com/subgraphs/name/convex-community/volume-celo"
)
SUBGRAPH_AURORA_API_PROD = (
    "https://api.thegraph.com/subgraphs/name/convex-community/volume-aurora"
)

SUBGRAPH_MAINNET_API_DEV = "https://api.thegraph.com/subgraphs/name/convex-community/volume-mainnet-test"
SUBGRAPH_ARBITRUM_API_DEV = "https://api.thegraph.com/subgraphs/name/convex-community/volume-arbitrum-test"
SUBGRAPH_AVALANCHE_API_DEV = "https://api.thegraph.com/subgraphs/name/convex-community/volume-avalanche-test"
SUBGRAPH_FANTOM_API_DEV = "https://api.thegraph.com/subgraphs/name/convex-community/volume-fantom-test"
SUBGRAPH_HARMONY_API_DEV = "https://api.thegraph.com/subgraphs/name/convex-community/volume-harmony-test"
SUBGRAPH_MATIC_API_DEV = "https://api.thegraph.com/subgraphs/name/convex-community/volume-matic-test"
SUBGRAPH_MOONBEAM_API_DEV = "https://api.thegraph.com/subgraphs/name/convex-community/volume-moonbeam-test"
SUBGRAPH_OPTIMISM_API_DEV = "https://api.thegraph.com/subgraphs/name/convex-community/volume-optimism-test"
SUBGRAPH_XDAI_API_DEV = (
    "https://api.thegraph.com/subgraphs/name/convex-community/volume-xdai-test"
)
SUBGRAPH_CELO_API_DEV = (
    "https://api.thegraph.com/subgraphs/name/convex-community/volume-celo-test"
)
SUBGRAPH_AURORA_API_DEV = "https://api.thegraph.com/subgraphs/name/convex-community/volume-aurora-test"

CONVEX_POOLS_SUBGRAPH_PROD = f"https://gateway.thegraph.com/api/{SUBGRAPHS_API_KEY}/subgraphs/id/6x6tQirWcrrESPPQU5cRkbtZnGBEAKHZrpJ7he9xqeth"
CONVEX_POOLS_SUBGRAPH_DEV = (
    "https://api.thegraph.com/subgraphs/name/convex-community/convex"
)

CURVE_SUBGRAPHS_PROD = {
    CHAIN_MAINNET: SUBGRAPH_MAINNET_API_PROD,
    CHAIN_ARBITRUM: SUBGRAPH_ARBITRUM_API_PROD,
    CHAIN_AVALANCHE: SUBGRAPH_AVALANCHE_API_PROD,
    CHAIN_FANTOM: SUBGRAPH_FANTOM_API_PROD,
    CHAIN_HARMONY: SUBGRAPH_HARMONY_API_PROD,
    CHAIN_MATIC: SUBGRAPH_MATIC_API_PROD,
    CHAIN_MOONBEAM: SUBGRAPH_MOONBEAM_API_PROD,
    CHAIN_OPTIMISM: SUBGRAPH_OPTIMISM_API_PROD,
    CHAIN_XDAI: SUBGRAPH_XDAI_API_PROD,
    CHAIN_CELO: SUBGRAPH_CELO_API_PROD,
    CHAIN_AURORA: SUBGRAPH_AURORA_API_PROD,
}

CURVE_SUBGRAPHS_DEV = {
    CHAIN_MAINNET: SUBGRAPH_MAINNET_API_DEV,
    CHAIN_ARBITRUM: SUBGRAPH_ARBITRUM_API_DEV,
    CHAIN_AVALANCHE: SUBGRAPH_AVALANCHE_API_DEV,
    CHAIN_FANTOM: SUBGRAPH_FANTOM_API_DEV,
    CHAIN_HARMONY: SUBGRAPH_HARMONY_API_DEV,
    CHAIN_MATIC: SUBGRAPH_MATIC_API_DEV,
    CHAIN_MOONBEAM: SUBGRAPH_MOONBEAM_API_DEV,
    CHAIN_OPTIMISM: SUBGRAPH_OPTIMISM_API_DEV,
    CHAIN_XDAI: SUBGRAPH_XDAI_API_DEV,
    CHAIN_CELO: SUBGRAPH_CELO_API_DEV,
    CHAIN_AURORA: SUBGRAPH_AURORA_API_DEV,
}

CURVE_DAO_SUBGRAPH_PROD = (
    "https://api.thegraph.com/subgraphs/name/convex-community/curve-dao"
)
CURVE_DAO_SUBGRAPH_DEV = (
    "https://api.thegraph.com/subgraphs/name/convex-community/curve-dao"
)

CRVUSD_SUBGRAPH_PROD = (
    "https://api.thegraph.com/subgraphs/name/convex-community/crvusd"
)

CRVUSD_SUBGRAPH_DEV = (
    "https://api.thegraph.com/subgraphs/name/convex-community/crvusd"
)

CURVE_POOLS = "CURVE_POOLS"
CONVEX_POOLS = "CONVEX_POOLS"
CURVE_DAO = "CURVE_DAO"
CRVUSD = "CRVUSD"

SUBGRAPHS_PROD = {
    CURVE_POOLS: CURVE_SUBGRAPHS_PROD,
    CURVE_DAO: CURVE_DAO_SUBGRAPH_PROD,
    CONVEX_POOLS: CONVEX_POOLS_SUBGRAPH_PROD,
    CRVUSD: CRVUSD_SUBGRAPH_PROD,
}

SUBGRAPHS_DEV = {
    CURVE_POOLS: CURVE_SUBGRAPHS_DEV,
    CURVE_DAO: CURVE_DAO_SUBGRAPH_DEV,
    CONVEX_POOLS: CONVEX_POOLS_SUBGRAPH_DEV,
    CRVUSD: CRVUSD_SUBGRAPH_DEV,
}
