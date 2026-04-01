from http_client import get_json

def check(contract_address: str) -> dict:
    """
    Analyzes trading behavior using the DexScreener API.
    Looks for wash trading (abnormal volume/liquidity ratios) 
    and extreme transaction velocity (pump/dump spikes).
    """
    print(f"[Transaction Detector] Analyzing trade patterns for {contract_address}...")

    # DexScreener provides a free, keyless API for DEX token data
    url = f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}"

    try:
        data = get_json(url)

        if not data.get("pairs"):
            return {
                "status": "Error",
                "reason": "No trading data found on DexScreener. Token might be dead or brand new."
            }

        # We grab the most active trading pair (usually the Uniswap WETH pair)
        main_pair = data["pairs"][0]
        
        # Extract the metrics we need
        liquidity_usd = main_pair.get("liquidity", {}).get("usd", 0)
        vol_24h = main_pair.get("volume", {}).get("h24", 0)
        vol_5m = main_pair.get("volume", {}).get("m5", 0)
        
        txns_24h = main_pair.get("txns", {}).get("h24", {})
        buys_24h = txns_24h.get("buys", 0)
        sells_24h = txns_24h.get("sells", 0)
        total_txns_24h = buys_24h + sells_24h

        print(f"  -> 24h Volume: ${vol_24h:,.2f} | Liquidity: ${liquidity_usd:,.2f}")
        print(f"  -> 5m Volume:  ${vol_5m:,.2f}")
        print(f"  -> 24h Txns:   {buys_24h} Buys / {sells_24h} Sells")

        # --- METRIC 1: Wash Trading (Turnover Ratio) ---
        # How many times did the entire liquidity pool trade today?
        turnover_ratio = 0
        if liquidity_usd > 0:
            turnover_ratio = vol_24h / liquidity_usd
            
        # --- METRIC 2: Pump & Dump Velocity ---
        # What percentage of the daily volume happened in just the last 5 minutes?
        velocity_spike_percent = 0
        if vol_24h > 0:
            velocity_spike_percent = (vol_5m / vol_24h) * 100

        # --- Evaluate the Risk ---
        status = "Pass"
        reason = "Trading volume and transaction velocity look organic."

        flags = []

        # 1. Check for Wash Trading
        if turnover_ratio > 100:
            flags.append(f"Extreme Wash Trading: Volume is {turnover_ratio:.1f}x larger than liquidity.")
            status = "High Risk"
        elif turnover_ratio > 30:
            flags.append(f"Suspicious Volume: Turnover ratio is high ({turnover_ratio:.1f}x). Possible bot wash trading.")
            if status == "Pass": status = "Warning"

        # 2. Check for Pump Spikes
        if velocity_spike_percent > 30 and vol_5m > 10000:
            flags.append(f"Massive Spike: {velocity_spike_percent:.1f}% of today's volume happened in the last 5 minutes.")
            status = "High Risk"

        # 3. Check for Buy/Sell HoneyPot anomalies
        if total_txns_24h > 50:
            if sells_24h == 0:
                flags.append("Zero Sells in 24h: 100% Buy ratio. This is a severe Honeypot indicator.")
                status = "High Risk"
            elif (buys_24h / total_txns_24h) > 0.95:
                flags.append("Abnormal Buy Ratio: Over 95% of transactions are buys. Selling may be restricted.")
                if status == "Pass": status = "Warning"

        if flags:
            reason = " | ".join(flags)

        return {
            "status": status,
            "reason": reason,
            "metrics": {
                "turnover_ratio": round(turnover_ratio, 2),
                "velocity_spike_5m": round(velocity_spike_percent, 2),
                "buy_ratio": round((buys_24h / total_txns_24h) * 100, 2) if total_txns_24h > 0 else 0
            }
        }

    except Exception as e:
        return {"status": "Error", "reason": f"API Error: {str(e)}"}

# --- Quick Test Block ---
if __name__ == "__main__":
    # Let's test PEPE token (which has massive, organic volume)
    test_target = "0x6982508145454Ce325dDbE47a25d4ec3d2311933"
    result = check(test_target)
    
    import json
    print(json.dumps(result, indent=4))