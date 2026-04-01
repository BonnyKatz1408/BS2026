from http_client import get_json


def _ethplorer_holders_count(contract_address: str) -> int:
    """
    getTopTokenHolders sometimes omits holdersCount; getTokenInfo includes it.
    """
    try:
        url = f"https://api.ethplorer.io/getTokenInfo/{contract_address}?apiKey=freekey"
        data = get_json(url)
        n = data.get("holdersCount")
        if n is None:
            return 0
        return int(n)
    except Exception:
        return 0


def check(contract_address: str) -> dict:
    """
    Analyzes the token distribution using the Ethplorer API.
    Checks if the top wallets hold a dangerous percentage of the supply.
    """
    print(f"[Holder Detector] Fetching top token holders for {contract_address}...")

    # Ethplorer provides a public 'freekey' for basic requests
    url = f"https://api.ethplorer.io/getTopTokenHolders/{contract_address}?apiKey=freekey&limit=10"

    try:
        data = get_json(url)

        if "error" in data:
            return {"status": "Error", "reason": "Failed to fetch holder data. Token might not exist."}

        holders = data.get("holders", [])
        if not holders:
            return {"status": "Error", "reason": "No holder data found."}
        total_holders = int(data.get("holdersCount", 0) or 0)
        if total_holders <= 0:
            total_holders = _ethplorer_holders_count(contract_address)

        # Known safe addresses (Burn addresses where tokens are permanently destroyed)
        safe_addresses = [
            "0x000000000000000000000000000000000000dead",
            "0x0000000000000000000000000000000000000000"
        ]

        total_top_percentage = 0.0
        highest_single_wallet = 0.0
        suspicious_wallets = 0

        print("  -> Top 10 Holders Breakdown:")
        
        # Loop through the top 10 wallets
        for holder in holders:
            address = holder.get("address", "").lower()
            share = holder.get("share", 0.0)

            # If it's a burn address, it's safe! We don't count it as a risk.
            if address in safe_addresses:
                print(f"     - {address[:8]}... (BURN ADDRESS) : {share:.2f}%")
                continue  

            print(f"     - {address[:8]}... : {share:.2f}%")
            total_top_percentage += share

            # Track the biggest single whale
            if share > highest_single_wallet:
                highest_single_wallet = share

            # Count how many individual wallets hold more than 10%
            if share > 10.0:
                suspicious_wallets += 1

        # Determine the final Risk Status
        status = "Pass"
        reason = f"Top holders control a safe amount ({total_top_percentage:.1f}%)."

        if highest_single_wallet > 20.0:
            status = "High Risk"
            reason = f"A single wallet holds {highest_single_wallet:.1f}% of the supply. Massive dump risk."
        elif total_top_percentage > 50.0:
            status = "Warning"
            reason = f"The top wallets control {total_top_percentage:.1f}% of the supply. High centralization."

        return {
            "status": status,
            "reason": reason,
            "top_10_concentration": round(total_top_percentage, 2),
            "highest_single_wallet": round(highest_single_wallet, 2),
            "suspicious_wallets_count": suspicious_wallets,
            "total_holders": total_holders
        }

    except Exception as e:
        return {"status": "Error", "reason": f"API Error: {str(e)}"}

# --- Quick Test Block ---
if __name__ == "__main__":
    # We will test SHIB again. SHIB famously sent 50% of its supply to 
    # Vitalik Buterin, who then burned it. Let's see if our detector catches the burn!
    test_target = "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE"
    result = check(test_target)
    
    import json
    print(json.dumps(result, indent=4))