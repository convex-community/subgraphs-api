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


REGISTRIES = {
    CHAIN_MAINNET: "0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5",
    CHAIN_MATIC: "0x094d12e5b541784701FD8d65F11fc0598FBC6332",
    CHAIN_ARBITRUM: "0x445FE580eF8d70FF569aB36e80c647af338db351",
    CHAIN_FANTOM: "0x0f854EA9F38ceA4B1c2FC79047E9D0134419D5d6",
    CHAIN_OPTIMISM: "0xC5cfaDA84E902aD92DD40194f0883ad49639b023",
    CHAIN_AVALANCHE: "0x8474DdbE98F5aA3179B3B3F5942D724aFcdec9f6",
    CHAIN_XDAI: "0x55E91365697EB8032F98290601847296eC847210",
    CHAIN_CELO: "0x0",
    CHAIN_AURORA: "0x5B5CFE992AdAC0C9D48E05854B2d91C73a003858",
    CHAIN_HARMONY: "0x0a53FaDa2d943057C47A301D25a4D9b3B8e01e8E",
    CHAIN_MOONBEAM: "0xC2b1DF84112619D190193E48148000e3990Bf627",
}

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
