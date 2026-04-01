def calculate(detector_results: dict, sim_results: dict) -> dict:
    """
    Ingests the outputs from all 4 static detectors and the dynamic simulation.
    Calculates a unified risk score from 0 (Safe) to 100 (Scam).
    """
    print("[Scoring Engine] Calculating unified risk profile...")
    
    score = 0
    driving_factors = []

    # --- 1. HONEYPOT & CODE ANALYSIS (calibrated) ---
    honeypot = detector_results.get("honeypot", {})
    sim_honeypot_signal = (
        sim_results.get("status") == "High Risk" or not sim_results.get("is_sellable", True)
    )
    if honeypot.get("status") == "High Risk" and sim_honeypot_signal:
        score += 80
        driving_factors.append("High Risk: Honeypot indicators are corroborated by simulation behavior.")
    elif honeypot.get("status") == "High Risk":
        score += 20
        driving_factors.append("Warning: Static honeypot indicators detected without dynamic sell-block confirmation.")
    elif honeypot.get("status") == "Warning":
        score += 15
        driving_factors.append(f"Warning: {honeypot.get('reason', 'Suspicious code patterns detected.')}")

    # --- 2. DYNAMIC SIMULATION & TAXES (+100 max) ---
    if sim_results.get("status") == "High Risk" or not sim_results.get("is_sellable", True):
        score += 100
        driving_factors.append("Critical: Token failed dynamic sell simulation (Honeypot) or has 100% sell tax.")
    else:
        buy_tax = sim_results.get("buy_tax", sim_results.get("max_buy_tax_detected", 0))
        sell_tax = sim_results.get("sell_tax", sim_results.get("max_sell_tax_detected", 0))
        
        if buy_tax > 15 or sell_tax > 15:
            score += 40
            driving_factors.append(f"High Risk: Abusive taxes detected (Buy: {buy_tax:.1f}%, Sell: {sell_tax:.1f}%).")
        elif buy_tax > 5 or sell_tax > 5:
            score += 15
            driving_factors.append(f"Warning: Moderate taxes (Buy: {buy_tax:.1f}%, Sell: {sell_tax:.1f}%).")

    # --- 3. LIQUIDITY ANALYSIS (+50 max) ---
    liquidity = detector_results.get("liquidity", {})
    if liquidity.get("status") == "High Risk":
        score += 50
        driving_factors.append("High Risk: Extremely low or missing Uniswap liquidity.")
    elif liquidity.get("status") == "Warning":
        score += 20
        driving_factors.append("Warning: Low liquidity. High risk of volatility or rugpull.")

    # --- 4. HOLDER DISTRIBUTION (+40 max) ---
    holders = detector_results.get("holders", {})
    if holders.get("status") == "High Risk":
        score += 40
        driving_factors.append("High Risk: A single wallet holds a massive percentage of the supply.")
    elif holders.get("status") == "Warning":
        score += 20
        driving_factors.append("Warning: Top 10 wallets control a centralized portion of the supply.")

    # --- 5. TRANSACTION BEHAVIOR (+40 max) ---
    txns = detector_results.get("transactions", {})
    if txns.get("status") == "High Risk":
        score += 40
        driving_factors.append("High Risk: Abnormal trading patterns (Bot wash trading or severe pump/dump).")
    elif txns.get("status") == "Warning":
        score += 20
        driving_factors.append("Warning: Suspicious transaction velocity or volume.")

    # --- 6. TOKEN AGE-TO-GROWTH CONTEXT (+30 max) ---
    age = detector_results.get("age", {})
    ratio = age.get("age_growth_ratio", None)
    if age.get("status") == "High Risk":
        score += 30
        if ratio is not None:
            driving_factors.append(
                f"High Risk: Age-growth mismatch ({age.get('age_days', 'unknown')}d, ratio {ratio})."
            )
        else:
            driving_factors.append(f"High Risk: Very new token age ({age.get('age_days', 'unknown')} days).")
    elif age.get("status") == "Warning":
        score += 15
        if ratio is not None:
            driving_factors.append(
                f"Warning: Fast growth versus age ({age.get('age_days', 'unknown')}d, ratio {ratio})."
            )
        else:
            driving_factors.append(f"Warning: Limited token age history ({age.get('age_days', 'unknown')} days).")

    # --- 7. MINTING / OWNER CONTROL (+50 max) ---
    minting = detector_results.get("minting", {})
    if minting.get("status") == "High Risk":
        score += 50
        driving_factors.append("High Risk: Owner-controlled minting/supply controls detected in contract logic.")
    elif minting.get("status") == "Warning":
        score += 25
        driving_factors.append("Warning: Contract includes pause/blacklist/mint control surfaces.")

    # --- 8. RUGPULL HEURISTICS (+60 max) ---
    rugpull = detector_results.get("rugpull", {})
    if rugpull.get("status") == "High Risk":
        score += 60
        driving_factors.append(
            f"High Risk: Rugpull heuristics triggered ({rugpull.get('reason', 'liquidity/ownership danger signals')})."
        )
    elif rugpull.get("status") == "Warning":
        score += 30
        driving_factors.append(
            f"Warning: Moderate rugpull indicators ({rugpull.get('reason', 'partial liquidity or holder concentration risk')})."
        )

    # --- 9. CONTEXTUAL SAFETY OFFSET ---
    # Mature tokens with deep liquidity and organic behavior should not be auto-labeled scam
    # based on one or two static red flags.
    taxes = detector_results.get("taxes", {})
    liquidity = detector_results.get("liquidity", {})
    holders = detector_results.get("holders", {})
    txns = detector_results.get("transactions", {})
    age = detector_results.get("age", {})

    mature_green_signals = 0
    if age.get("status") == "Pass" and (age.get("age_days") or 0) >= 180:
        mature_green_signals += 1
    if liquidity.get("status") == "Pass" and (liquidity.get("eth_in_pool") or 0) >= 200:
        mature_green_signals += 1
    if holders.get("status") == "Pass":
        mature_green_signals += 1
    if txns.get("status") == "Pass":
        mature_green_signals += 1
    if taxes.get("status") == "Pass":
        mature_green_signals += 1

    if mature_green_signals >= 4:
        score = max(0, score - 25)
        driving_factors.append("Context: Strong maturity/liquidity/activity signals reduce scam likelihood.")

    # --- FINAL CALCULATION ---
    # Cap the maximum score at exactly 100
    final_score = min(score, 100)

    # Assign a human-readable risk tier
    if final_score >= 80:
        risk_level = "CRITICAL"
    elif final_score >= 50:
        risk_level = "HIGH RISK"
    elif final_score >= 20:
        risk_level = "MEDIUM RISK"
    else:
        risk_level = "LOW RISK (SAFE)"

    return {
        "numeric_score": final_score,
        "risk_level": risk_level,
        "driving_factors": driving_factors
    }

# --- Quick Test Block ---
if __name__ == "__main__":
    # Let's mock the data for a token that has good code, but terrible taxes and bad distribution
    mock_detectors = {
        "honeypot": {"status": "Pass"},
        "liquidity": {"status": "Warning"}, # +20
        "holders": {"status": "High Risk"}, # +40
        "transactions": {"status": "Pass"}
    }
    
    mock_simulation = {
        "status": "Warning",
        "is_sellable": True,
        "buy_tax": 20.0, # +40
        "sell_tax": 20.0
    }
    
    result = calculate(mock_detectors, mock_simulation)
    
    import json
    print(json.dumps(result, indent=4))