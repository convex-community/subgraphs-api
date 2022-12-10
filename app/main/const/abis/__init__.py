import os
import json

location = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__))
)
VOTING_ABI = json.load(open(os.path.join(location, "Voting.json"), "r"))
AGENT_ABI = json.load(open(os.path.join(location, "Agent.json"), "r"))
GAUGE_CONTROLLER_ABI = json.load(
    open(os.path.join(location, "GaugeController.json"), "r")
)
POOL_OWNER_ABI = json.load(open(os.path.join(location, "PoolOwner.json"), "r"))
VESTING_ESCROW_FACTORY_ABI = json.load(
    open(os.path.join(location, "VestingEscrowFactory.json"), "r")
)
VOTING_ESCROW_ABI = json.load(
    open(os.path.join(location, "VotingEscrow.json"), "r")
)
STABLE_SWAP_PROXY_ABI = json.load(
    open(os.path.join(location, "StableProxy.json"), "r")
)
CRYPTO_SWAP_PROXY_ABI = json.load(
    open(os.path.join(location, "CryptoSwapOwnerProxy.json"), "r")
)
LP_BURNER_ABI = json.load(open(os.path.join(location, "LPBurner.json"), "r"))
ROLES_ABI = json.load(open(os.path.join(location, "Roles.json"), "r"))

OWNERSHIP_AGENT = "0x40907540d8a6c65c637785e8f8b742ae6b0b9968"
PARAMETER_AGENT = "0x4eeb3ba4f221ca16ed4a0cc7254e2e32df948c5f"
GAUGE_CONTROLLER = "0x2f50d538606fa9edd2b11e2446beb18c9d5846bb"
POOL_OWNER = "0xecb456ea5365865ebab8a2661b0c503410e9b347"
VESTING_ESCROW_FACTORY = "0xe3997288987e6297ad550a69b31439504f513267"
LP_BURNER = "0xaa42c0cd9645a58dfeb699ccaefbd30f19b1ff81"
VOTING_ESCROW = "0x5f3b5dfeb7b28cdbd7faba78963ee202a494e2a2"
ROLES = "0xb7030b04944832d7b8aff227b325b51ba5074013"
STABLE_SWAP_PROXIES = [
    "0x56295b752e632f74a6526988eace33c25c52c623",
    "0x3f4232107ff437bcd7ea9abc134ad553efeddaff",
    "0x6e8f6d1da6232d5e40b0b8758a0145d6c5123eb7",
]
CRYPTO_SWAP_PROXIES = ["0x5a8fdc979ba9b6179916404414f7ba4d8b77c8a1"]

ABI_MAP = {
    OWNERSHIP_AGENT: AGENT_ABI,
    PARAMETER_AGENT: AGENT_ABI,
    GAUGE_CONTROLLER: GAUGE_CONTROLLER_ABI,
    POOL_OWNER: POOL_OWNER_ABI,
    VESTING_ESCROW_FACTORY: VESTING_ESCROW_FACTORY_ABI,
    LP_BURNER: LP_BURNER_ABI,
    VOTING_ESCROW: VOTING_ESCROW_ABI,
    ROLES: ROLES_ABI,
}
ABI_MAP.update({proxy: STABLE_SWAP_PROXY_ABI for proxy in STABLE_SWAP_PROXIES})
ABI_MAP.update({proxy: CRYPTO_SWAP_PROXY_ABI for proxy in CRYPTO_SWAP_PROXIES})
