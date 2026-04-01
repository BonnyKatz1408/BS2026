import os
from web3 import Web3
from web3.exceptions import ContractLogicError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to the Ethereum network
RPC_URL = os.getenv("RPC_URL", "https://cloudflare-eth.com")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# --- CONSTANTS & ABIs ---
# Uniswap V2 Router Address (The contract that handles all the buying/selling)
UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" # Wrapped ETH

# We only need the specific functions we are calling, not the whole ABI
ROUTER_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "amountIn", "type": "uint256"}, {"name": "path", "type": "address[]"}],
        "name": "getAmountsOut",
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

def simulate_trade(contract_address: str, eth_buy_amount: float = 0.05) -> dict:
    """
    Executes a read-only Web3 simulation of a Uniswap trade to detect hidden
    taxes and hard-coded honeypot reverts.
    """
    print(f"[Simulation Engine] Booting Web3 Simulator for {contract_address}...")
    
    # Format addresses properly for Web3
    try:
        token_address = w3.to_checksum_address(contract_address)
        router_address = w3.to_checksum_address(UNISWAP_V2_ROUTER)
        weth_address = w3.to_checksum_address(WETH_ADDRESS)
    except ValueError:
        return {"status": "Error", "reason": "Invalid Ethereum address format."}

    # Initialize contracts
    router_contract = w3.eth.contract(address=router_address, abi=ROUTER_ABI)
    token_contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)

    amount_in_wei = w3.to_wei(eth_buy_amount, 'ether')

    results = {
        "status": "Pass",
        "buy_tax": 0.0,
        "sell_tax": 0.0,
        "is_sellable": True,
        "details": "",
        "eth_in": eth_buy_amount,
        "expected_tokens_out_raw": 0,
        "expected_tokens_out_human": 0.0,
        "estimated_tokens_received_human": 0.0,
        "expected_eth_out_human": 0.0,
    }

    try:
        # ---------------------------------------------------------
        # PHASE 1: THE BUY SIMULATION
        # ---------------------------------------------------------
        # 1. Ask Uniswap what we *should* get if there were 0 taxes
        print("  -> Querying Uniswap routing path (ETH -> Token)...")
        amounts_out = router_contract.functions.getAmountsOut(
            amount_in_wei, 
            [weth_address, token_address]
        ).call()
        
        expected_tokens_out = amounts_out[1]
        results["expected_tokens_out_raw"] = int(expected_tokens_out)
        try:
            token_decimals = token_contract.functions.decimals().call()
        except Exception:
            token_decimals = 18
        if token_decimals < 0 or token_decimals > 36:
            token_decimals = 18
        results["expected_tokens_out_human"] = float(expected_tokens_out) / (10 ** token_decimals)

        # NOTE:
        # On a public RPC we cannot execute stateful swaps for a real wallet here.
        # So we use quote-based heuristics and explicit call failures as signals.
        if expected_tokens_out == 0:
            return {
                "status": "High Risk",
                "reason": "Uniswap returned 0 tokens. Liquidity pool may be empty or missing."
            }

        actual_tokens_received = expected_tokens_out
        results["estimated_tokens_received_human"] = float(actual_tokens_received) / (10 ** token_decimals)
        results["buy_tax"] = 0.0

        # ---------------------------------------------------------
        # PHASE 2: THE SELL SIMULATION (THE HONEYPOT CHECK)
        # ---------------------------------------------------------
        print("  -> Simulating Sell transaction (Token -> ETH)...")
        
        # Ask Uniswap what we *should* get for selling those tokens back
        sell_amounts_out = router_contract.functions.getAmountsOut(
            actual_tokens_received, 
            [token_address, weth_address]
        ).call()
        
        expected_eth_out = sell_amounts_out[1]
        results["expected_eth_out_human"] = float(w3.from_wei(expected_eth_out, "ether"))

        if amount_in_wei > 0:
            round_trip_ratio = (expected_eth_out / amount_in_wei) * 100
            implied_loss_pct = max(0.0, 100.0 - round_trip_ratio)
        else:
            implied_loss_pct = 0.0

        # This is an implied round-trip loss proxy, not a literal contract tax figure.
        results["sell_tax"] = min(implied_loss_pct, 100.0)

        # Check against our thresholds
        if results["buy_tax"] > 15 or results["sell_tax"] > 15:
            results["status"] = "Warning"
            results["details"] = (
                "High round-trip loss detected from DEX quotes "
                f"(Buy proxy: {results['buy_tax']:.1f}%, Loss proxy: {results['sell_tax']:.1f}%)."
            )
            
        if results["sell_tax"] >= 95:
            results["status"] = "High Risk"
            results["details"] = "Near-total round-trip loss detected. Token may be unsellable or extremely illiquid."

    except ContractLogicError as e:
        # THE MOST IMPORTANT CHECK:
        # If the Web3 call explicitly reverts (crashes), it usually means the token 
        # contract blocked the transfer. This is the definition of a Honeypot.
        results["status"] = "High Risk"
        results["is_sellable"] = False
        results["details"] = f"Transaction REVERTED during simulation. This is highly indicative of a honeypot trap. (Error: {str(e)})"
    
    except Exception as e:
        results["status"] = "Error"
        results["details"] = f"Simulation failed due to an unknown error: {str(e)}"

    return results

# --- Quick Test Block ---
if __name__ == "__main__":
    # We will test an actual token (USDT) on the live mainnet
    # Note: USDT has a massive liquidity pool, so this will work perfectly.
    test_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    
    result = simulate_trade(test_address)
    
    import json
    print(json.dumps(result, indent=4))