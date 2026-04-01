from http_client import get_json


def fetch_goplus_token(contract_address: str) -> dict:
    """Raw GoPlus token_security row for an address, or {} if unavailable."""
    url = f"https://api.gopluslabs.io/api/v1/token_security/1?contract_addresses={contract_address.lower()}"
    try:
        data = get_json(url)
        if data.get("code") != 1 or not data.get("result"):
            return {}
        row = data["result"].get(contract_address.lower(), {})
        return row if isinstance(row, dict) else {}
    except Exception:
        return {}


def check(contract_address: str) -> dict:
    """
    Queries the GoPlus Security API to extract the statically 
    programmed buy and sell taxes directly from the contract code.
    """
    print(f"[Tax Calculator] Extracting hardcoded tax rates for {contract_address}...")

    try:
        token_data = fetch_goplus_token(contract_address)

        if not token_data:
            return {
                "status": "Error",
                "reason": "Token not found in GoPlus security database. It may be unverified.",
                "buy_tax": 0.0,
                "sell_tax": 0.0
            }

        # Extract taxes (GoPlus returns them as strings like "0.05" for 5%, or empty if 0)
        raw_buy_tax = token_data.get("buy_tax", "0")
        raw_sell_tax = token_data.get("sell_tax", "0")

        # Convert to clean floats (Handle edge cases where the API returns empty strings)
        buy_tax = float(raw_buy_tax) * 100 if raw_buy_tax else 0.0
        sell_tax = float(raw_sell_tax) * 100 if raw_sell_tax else 0.0

        # --- Evaluate the Risk ---
        status = "Pass"
        reason = f"Standard taxes detected (Buy: {buy_tax:.1f}%, Sell: {sell_tax:.1f}%)."

        if buy_tax >= 50.0 or sell_tax >= 50.0:
            status = "High Risk"
            reason = f"Maliciously high taxes hardcoded into the contract (Buy: {buy_tax:.1f}%, Sell: {sell_tax:.1f}%)."
        elif buy_tax > 10.0 or sell_tax > 10.0:
            status = "Warning"
            reason = f"High trading taxes detected (Buy: {buy_tax:.1f}%, Sell: {sell_tax:.1f}%). Proceed with caution."

        return {
            "status": status,
            "reason": reason,
            "buy_tax": round(buy_tax, 2),
            "sell_tax": round(sell_tax, 2),
            "is_honeypot": token_data.get("is_honeypot") == "1"
        }

    except Exception as e:
        return {
            "status": "Error",
            "reason": f"API Error: {str(e)}",
            "buy_tax": 0.0,
            "sell_tax": 0.0
        }

# --- Quick Test Block ---
if __name__ == "__main__":
    # Let's test Cult DAO (CULT), a token famous for having a hardcoded 0.4% tax
    test_target = "0xf0f9D895aCa5c8678f706FB8216fa22957685A13"
    result = check(test_target)
    
    import json
    print(json.dumps(result, indent=4))