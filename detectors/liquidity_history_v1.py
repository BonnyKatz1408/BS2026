import os
import time
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()
RPC_URL = os.getenv("RPC_URL", "https://rpc.ankr.com/eth")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Uniswap V2 factory (Ethereum mainnet)
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

BURN_LIKE_ADDRESSES = {
    # Not used in this file directly; kept for possible future extension.
    "0x0000000000000000000000000000000000000000",
    "0x000000000000000000000000000000000000dead",
}


def _ts_label(ts: int) -> str:
    # Short label similar to chart time-axis.
    try:
        return time.strftime("%H:%M", time.gmtime(ts))
    except Exception:
        return str(ts)


def get_liquidity_series(
    contract_address: str,
    points: int = 24,
    window_hours: float = 12.0,
    avg_block_time_sec: int = 12,
) -> dict:
    """
    Fetch a lightweight historical liquidity series by sampling Uniswap V2 pair reserves
    at earlier block numbers via RPC.

    Output shape:
    - status: Success/Error
    - pair_address
    - labels: list[str]
    - liquidity_eth: list[float] (WETH reserve in ETH terms)
    """
    try:
        token_address = w3.to_checksum_address(contract_address)
        weth_address = w3.to_checksum_address(WETH_ADDRESS)

        factory_contract = w3.eth.contract(address=UNISWAP_V2_FACTORY, abi=FACTORY_ABI)
        pair_address = factory_contract.functions.getPair(token_address, weth_address).call()

        if not pair_address or pair_address.lower() == "0x0000000000000000000000000000000000000000":
            return {"status": "Error", "reason": "No Uniswap V2 pair found for token/WETH."}

        pair_meta = w3.eth.contract(address=pair_address, abi=PAIR_ABI)
        token0 = pair_meta.functions.token0().call()
        weth_is_reserve0 = token0.lower() == weth_address.lower()

        # Keep sampling budget reasonable to avoid RPC timeouts.
        points = int(points)
        points = max(6, min(points, 60))
        window_hours = float(window_hours)
        window_hours = max(0.5, min(window_hours, 72.0))

        latest_block = int(w3.eth.block_number)
        window_seconds = window_hours * 3600.0
        if points <= 1:
            block_step = 1
        else:
            block_step = max(1, int((window_seconds / (points - 1)) / avg_block_time_sec))

        # Chronological samples
        sample_blocks = [max(0, latest_block - (points - 1 - i) * block_step) for i in range(points)]

        labels: list[str] = []
        liquidity_eth: list[float] = []

        for b in sample_blocks:
            try:
                reserves = pair_meta.functions.getReserves().call(block_identifier=b)
                reserve0_raw = reserves[0]
                reserve1_raw = reserves[1]
                ts_last = reserves[2]
                weth_reserve_raw = reserve0_raw if weth_is_reserve0 else reserve1_raw

                # Liquidity proxy: WETH reserve in ETH terms.
                liq_eth = float(w3.from_wei(weth_reserve_raw, "ether"))
                liquidity_eth.append(round(liq_eth, 6))

                # Uniswap returns the last block timestamp used to compute reserves.
                labels.append(_ts_label(int(ts_last)))
            except Exception:
                # Some historical blocks (before pair creation / RPC gaps) can fail.
                # Skip bad samples instead of failing the whole series.
                continue

        # Fallback: ensure we still return useful data if historical sampling failed.
        if not labels or not liquidity_eth:
            try:
                reserves = pair_meta.functions.getReserves().call()
                reserve0_raw = reserves[0]
                reserve1_raw = reserves[1]
                ts_last = reserves[2]
                weth_reserve_raw = reserve0_raw if weth_is_reserve0 else reserve1_raw
                liq_eth = float(w3.from_wei(weth_reserve_raw, "ether"))
                labels = [_ts_label(int(ts_last))]
                liquidity_eth = [round(liq_eth, 6)]
            except Exception as e:
                return {"status": "Error", "reason": f"Liquidity series fetch failed: {str(e)}"}

        return {
            "status": "Success",
            "pair_address": pair_address,
            "window_hours": window_hours,
            "points": points,
            "labels": labels,
            "liquidity_eth": liquidity_eth,
        }

    except Exception as e:
        return {"status": "Error", "reason": f"Liquidity series fetch failed: {str(e)}"}


if __name__ == "__main__":
    # Quick local test.
    print(get_liquidity_series("0x6982508145454Ce325dDbE47a25d4ec3d2311933", points=12, window_hours=6))

