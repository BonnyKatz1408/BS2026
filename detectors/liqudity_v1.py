import os
from web3 import Web3
from dotenv import load_dotenv
from http_client import get_json

# Load environment variables
load_dotenv()
RPC_URL = os.getenv("RPC_URL", "https://rpc.ankr.com/eth")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# --- CONSTANTS & ABIs ---
# Uniswap V2 Factory (The contract that creates and tracks all liquidity pools)
UNISWAP_V2_FACTORY = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"

FACTORY_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "tokenA", "type": "address"}, {"name": "tokenB", "type": "address"}],
        "name": "getPair",
        "outputs": [{"name": "pair", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
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
            {"name": "_blockTimestampLast", "type": "uint32"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token0",
        "outputs": [{"name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]


def _fallback_dexscreener_liquidity(contract_address: str) -> dict:
    """
    Fallback when Uniswap V2 WETH pair is missing/unusable.
    Uses DexScreener best pair liquidity.
    """
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"
        data = get_json(url, timeout=20)
        pairs = data.get("pairs", []) or []
        if not pairs:
            return {
                "status": "High Risk",
                "reason": "No liquidity pair found on DexScreener for this token.",
                "pair_address": None,
                "eth_in_pool": 0.0,
                "liquidity_usd": 0.0,
                "source": "dexscreener",
            }

        # Pick pair with highest USD liquidity.
        def liq_usd(p):
            try:
                return float((p.get("liquidity") or {}).get("usd") or 0.0)
            except Exception:
                return 0.0

        best = max(pairs, key=liq_usd)
        liquidity = best.get("liquidity") or {}
        liquidity_usd = float(liquidity.get("usd") or 0.0)

        quote = best.get("quoteToken") or {}
        quote_symbol = str(quote.get("symbol") or "").upper()
        eth_in_pool = None

        # If quote side is WETH/ETH, DexScreener quote liquidity approximates ETH side depth.
        if quote_symbol in {"WETH", "ETH"}:
            try:
                q = liquidity.get("quote")
                if q is not None:
                    eth_in_pool = float(q)
            except Exception:
                eth_in_pool = None

        status = "Pass"
        if liquidity_usd < 50_000:
            status = "High Risk"
            reason = f"Very low DEX liquidity (${liquidity_usd:,.0f})."
        elif liquidity_usd < 250_000:
            status = "Warning"
            reason = f"Moderate DEX liquidity (${liquidity_usd:,.0f})."
        else:
            reason = f"Healthy DEX liquidity (${liquidity_usd:,.0f})."

        return {
            "status": status,
            "reason": reason,
            "pair_address": best.get("pairAddress"),
            "eth_in_pool": round(eth_in_pool, 4) if isinstance(eth_in_pool, float) else None,
            "liquidity_usd": round(liquidity_usd, 2),
            "dex_id": best.get("dexId"),
            "source": "dexscreener",
        }
    except Exception as e:
        return {
            "status": "Error",
            "reason": f"DexScreener fallback failed: {str(e)}",
            "pair_address": None,
            "eth_in_pool": 0.0,
            "liquidity_usd": 0.0,
            "source": "dexscreener",
        }

def check(contract_address: str) -> dict:
    """
    Checks the status of the Uniswap V2 Liquidity Pool for the given token.
    Evaluates pool size and sets up the LP lock analysis.
    """
    print(f"[Liquidity Detector] Locating Uniswap Pool for {contract_address}...")
    
    try:
        token_address = w3.to_checksum_address(contract_address)
        weth_address = w3.to_checksum_address(WETH_ADDRESS)
        factory_contract = w3.eth.contract(address=UNISWAP_V2_FACTORY, abi=FACTORY_ABI)
        
        # STEP 1: Ask Uniswap if a Liquidity Pool even exists for this token
        pair_address = factory_contract.functions.getPair(token_address, weth_address).call()
        
        if pair_address == "0x0000000000000000000000000000000000000000":
            # Many legitimate tokens trade primarily on non-V2 paths (V3/other DEXes).
            return _fallback_dexscreener_liquidity(contract_address)

        print(f"  -> Found Liquidity Pool at: {pair_address}")
        
        # STEP 2: Connect to the specific Pair Contract and get the reserves
        pair_contract = w3.eth.contract(address=pair_address, abi=PAIR_ABI)
        reserves = pair_contract.functions.getReserves().call()
        token0_address = pair_contract.functions.token0().call()
        
        # Figure out which reserve is WETH and which is the Token
        if token0_address == weth_address:
            weth_reserve_raw = reserves[0]
        else:
            weth_reserve_raw = reserves[1]
            
        eth_in_pool = float(w3.from_wei(weth_reserve_raw, 'ether'))
        print(f"  -> Pool contains {eth_in_pool:.2f} ETH")

        # STEP 3: Analyze the Liquidity Size
        status = "Pass"
        reason = f"Healthy liquidity detected ({eth_in_pool:.2f} ETH)."
        
        if eth_in_pool < 1.0:
            status = "High Risk"
            reason = f"Extremely low liquidity ({eth_in_pool:.2f} ETH). Massive risk of price manipulation or rugpull."
        elif eth_in_pool < 5.0:
            status = "Warning"
            reason = f"Low liquidity ({eth_in_pool:.2f} ETH). High volatility expected."

        # Note for LP Locking: To check if the LP is locked, we would need to check the 
        # balance of `pair_address` in the dev's wallet vs the burn address. 
        # For a full V1, checking the raw pool size is the critical first step.

        return {
            "status": status,
            "reason": reason,
            "pair_address": pair_address,
            "eth_in_pool": round(eth_in_pool, 2),
            "liquidity_usd": None,
            "source": "uniswap_v2"
        }

    except Exception as e:
        # Web3 may fail on some RPCs/tokens; fallback to market data instead of hard-error 0.
        fallback = _fallback_dexscreener_liquidity(contract_address)
        if fallback.get("status") != "Error":
            return fallback
        return {"status": "Error", "reason": f"Web3 Error: {str(e)}"}

# --- Quick Test Block ---
if __name__ == "__main__":
    # Let's test a massive token like SHIB to see a massive pool
    test_target = "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE" 
    result = check(test_target)
    
    import json
    print(json.dumps(result, indent=4))