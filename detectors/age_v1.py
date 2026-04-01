import os
import time
from dotenv import load_dotenv
from http_client import get_json

load_dotenv()
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")


def _get_block_timestamp(block_number: int) -> int:
    hex_block = hex(block_number)
    url = (
        "https://api.etherscan.io/v2/api"
        f"?chainid=1&module=proxy&action=eth_getBlockByNumber&tag={hex_block}"
        f"&boolean=true&apikey={ETHERSCAN_API_KEY}"
    )
    data = get_json(url)
    result = data.get("result", {})
    ts_hex = result.get("timestamp", "0x0")
    return int(ts_hex, 16)


def check(contract_address: str) -> dict:
    """
    Estimates token age from first transaction block and marks newer tokens as riskier.
    """
    print(f"[Age Detector] Estimating token age for {contract_address}...")

    if not ETHERSCAN_API_KEY:
        return {"status": "Error", "reason": "ETHERSCAN_API_KEY missing in .env", "age_days": None}

    try:
        txlist_url = (
            "https://api.etherscan.io/v2/api"
            f"?chainid=1&module=account&action=txlist&address={contract_address}"
            "&startblock=0&endblock=99999999&page=1&offset=1&sort=asc"
            f"&apikey={ETHERSCAN_API_KEY}"
        )
        data = get_json(txlist_url)

        if data.get("status") == "0" or not data.get("result"):
            return {
                "status": "Warning",
                "reason": "Could not determine first tx history; token may be very new or inactive.",
                "age_days": None,
            }

        first_tx = data["result"][0]
        first_block = int(first_tx.get("blockNumber", "0"))
        if first_block <= 0:
            return {"status": "Warning", "reason": "Invalid first block from Etherscan.", "age_days": None}

        created_ts = _get_block_timestamp(first_block)
        if created_ts <= 0:
            return {"status": "Warning", "reason": "Could not fetch creation block timestamp.", "age_days": None}

        now_ts = int(time.time())
        age_days = max(0, int((now_ts - created_ts) / 86400))

        if age_days < 7:
            status = "High Risk"
            reason = f"Very new token ({age_days} days old). New contracts carry higher rug/honeypot risk."
        elif age_days < 30:
            status = "Warning"
            reason = f"Relatively new token ({age_days} days old). Treat with caution."
        else:
            status = "Pass"
            reason = f"Token has market history ({age_days} days old)."

        return {
            "status": status,
            "reason": reason,
            "age_days": age_days,
            "first_seen_block": first_block,
        }
    except Exception as e:
        return {"status": "Error", "reason": f"Age detection failed: {str(e)}", "age_days": None}

