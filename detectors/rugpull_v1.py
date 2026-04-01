import os
from dotenv import load_dotenv
from web3 import Web3
from http_client import get_json

load_dotenv()
RPC_URL = os.getenv("RPC_URL", "https://rpc.ankr.com/eth")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

UNISWAP_V2_FACTORY = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
BURN_ADDRESSES = {
    "0x0000000000000000000000000000000000000000",
    "0x000000000000000000000000000000000000dead",
}

FACTORY_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "tokenA", "type": "address"}, {"name": "tokenB", "type": "address"}],
        "name": "getPair",
        "outputs": [{"name": "pair", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]

PAIR_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"name": "_reserve0", "type": "uint112"},
            {"name": "_reserve1", "type": "uint112"},
            {"name": "_blockTimestampLast", "type": "uint32"},
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token0",
        "outputs": [{"name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]


def _fetch_top_holders(contract_address: str) -> list[dict]:
    url = f"https://api.ethplorer.io/getTopTokenHolders/{contract_address}?apiKey=freekey&limit=10"
    data = get_json(url)
    if "error" in data:
        return []
    return data.get("holders", [])


def check(contract_address: str) -> dict:
    """
    Rugpull heuristics:
    1) LP token concentration (if deployer/EOA can remove liquidity)
    2) Top holder concentration > 50%
    3) Sell-side restrictions signals from holder imbalance
    """
    print(f"[Rugpull Detector] Running rugpull heuristics for {contract_address}...")
    try:
        token_address = w3.to_checksum_address(contract_address)
        weth_address = w3.to_checksum_address(WETH_ADDRESS)
        factory_contract = w3.eth.contract(address=UNISWAP_V2_FACTORY, abi=FACTORY_ABI)
        pair_address = factory_contract.functions.getPair(token_address, weth_address).call()

        status = "Pass"
        reasons = []
        lp_risk = "Unknown"
        lp_burn_percent = None

        if pair_address == "0x0000000000000000000000000000000000000000":
            status = "Warning"
            reasons.append("No Uniswap V2 pair found. Cannot assess LP-lock risk through this path.")
        else:
            pair = w3.eth.contract(address=pair_address, abi=ERC20_ABI)
            pair_meta = w3.eth.contract(address=pair_address, abi=PAIR_ABI)
            total_lp = pair.functions.totalSupply().call()
            reserves = pair_meta.functions.getReserves().call()
            token0 = pair_meta.functions.token0().call()
            weth_reserve_raw = reserves[0] if token0.lower() == weth_address.lower() else reserves[1]
            eth_in_pool = float(w3.from_wei(weth_reserve_raw, "ether"))

            burn_lp = 0
            for burn in BURN_ADDRESSES:
                burn_lp += pair.functions.balanceOf(w3.to_checksum_address(burn)).call()

            if total_lp > 0:
                lp_burn_percent = (burn_lp / total_lp) * 100
                if lp_burn_percent < 20:
                    status = "High Risk"
                    lp_risk = "High"
                    reasons.append(
                        f"Low burned LP share ({lp_burn_percent:.2f}%). Owner may retain liquidity removal power."
                    )
                elif lp_burn_percent < 60:
                    if status != "High Risk":
                        status = "Warning"
                    lp_risk = "Medium"
                    reasons.append(f"Partial LP burn ({lp_burn_percent:.2f}%). Liquidity lock confidence is limited.")
                else:
                    lp_risk = "Low"
                    reasons.append(f"High LP burn share ({lp_burn_percent:.2f}%). Lower immediate rugpull risk.")
            else:
                if status != "High Risk":
                    status = "Warning"
                lp_risk = "Medium"
                reasons.append("LP token total supply is zero/unreadable. LP ownership confidence is low.")

        holders = _fetch_top_holders(contract_address)
        top10 = 0.0
        max_wallet = 0.0
        for holder in holders:
            address = holder.get("address", "").lower()
            share = float(holder.get("share", 0) or 0)
            if address in BURN_ADDRESSES:
                continue
            top10 += share
            max_wallet = max(max_wallet, share)

        if top10 > 50:
            if status != "High Risk":
                status = "Warning"
            reasons.append(f"Top holders concentration is high ({top10:.2f}%).")
        if max_wallet > 25:
            status = "High Risk"
            reasons.append(f"Single wallet controls {max_wallet:.2f}% of supply.")

        # Context-aware downgrade:
        # Large, deep-liquidity and decentralized tokens can be legitimate even without burned LP.
        if (
            status == "High Risk"
            and lp_burn_percent is not None
            and lp_burn_percent < 20
            and eth_in_pool >= 1000
            and top10 <= 50
            and max_wallet <= 20
        ):
            status = "Warning"
            lp_risk = "Medium"
            reasons.append(
                "Context adjustment: Deep liquidity and broad holder distribution reduce immediate rugpull likelihood."
            )

        if not reasons:
            reasons.append("No strong rugpull signals triggered by current heuristics.")

        return {
            "status": status,
            "reason": " | ".join(reasons),
            "pair_address": pair_address if pair_address != "0x0000000000000000000000000000000000000000" else None,
            "lp_risk": lp_risk,
            "lp_burn_percent": round(lp_burn_percent, 2) if lp_burn_percent is not None else None,
            "eth_in_pool": round(eth_in_pool, 2) if pair_address != "0x0000000000000000000000000000000000000000" else None,
            "top_10_concentration": round(top10, 2),
            "highest_single_wallet": round(max_wallet, 2),
        }
    except Exception as e:
        return {
            "status": "Error",
            "reason": f"Rugpull detector failed: {str(e)}",
            "pair_address": None,
            "lp_risk": "Unknown",
            "lp_burn_percent": None,
            "top_10_concentration": None,
            "highest_single_wallet": None,
        }

