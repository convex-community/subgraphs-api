CHAIN_MAINNET = "mainnet"
CHAIN_ARBITRUM = "arbitrum"
CHAIN_AVALANCHE = "avalanche"
CHAIN_FANTOM = "fantom"
CHAIN_HARMONY = "harmony"
CHAIN_MATIC = "matic"
CHAIN_MOONBEAM = "moonbeam"
CHAIN_OPTIMISM = "optimism"
CHAIN_XDAI = "xdai"

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
]

SUBGRAPH_MAINNET_API_PROD = "https://api.thegraph.com/subgraphs/name/convex-community/volume-mainnet-test"
SUBGRAPH_ARBITRUM_API_PROD = "https://api.thegraph.com/subgraphs/name/convex-community/volume-arbitrum-test"
SUBGRAPH_AVALANCHE_API_PROD = "https://api.thegraph.com/subgraphs/name/convex-community/volume-avalanche-test"
SUBGRAPH_FANTOM_API_PROD = "https://api.thegraph.com/subgraphs/name/convex-community/volume-fantom-test"
SUBGRAPH_HARMONY_API_PROD = "https://api.thegraph.com/subgraphs/name/convex-community/volume-harmony-test"
SUBGRAPH_MATIC_API_PROD = "https://api.thegraph.com/subgraphs/name/convex-community/volume-matic-test"
SUBGRAPH_MOONBEAM_API_PROD = "https://api.thegraph.com/subgraphs/name/convex-community/volume-moonbeam-test"
SUBGRAPH_OPTIMISM_API_PROD = "https://api.thegraph.com/subgraphs/name/convex-community/volume-optimism-test"
SUBGRAPH_XDAI_API_PROD = (
    "https://api.thegraph.com/subgraphs/name/convex-community/volume-xdai-test"
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

CONVEX_POOLS_SUBGRAPH_PROD = (
    "https://api.thegraph.com/subgraphs/name/convex-community/curve-pools"
)
CONVEX_POOLS_SUBGRAPH_DEV = (
    "https://api.thegraph.com/subgraphs/name/convex-community/curve-pools"
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
}

CURVE_POOLS = "CURVE_POOLS"
CONVEX_POOLS = "CONVEX_POOLS"

SUBGRAPHS_PROD = {
    CURVE_POOLS: CURVE_SUBGRAPHS_PROD,
    CONVEX_POOLS: CONVEX_POOLS_SUBGRAPH_PROD,
}

SUBGRAPHS_DEV = {
    CURVE_POOLS: CURVE_SUBGRAPHS_DEV,
    CONVEX_POOLS: CONVEX_POOLS_SUBGRAPH_DEV,
}

DAY = 3600 * 24
WEEK = 3600 * 24 * 7
