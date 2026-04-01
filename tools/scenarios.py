import json
# Import the engine we built earlier
from engine import simulate_trade

def run_stress_tests(contract_address: str) -> dict:
    """
    Runs multiple simulation scenarios to catch dynamic taxes, 
    anti-whale traps, and size-based honeypots.
    """
    print(f"[Scenario Runner] Initiating dynamic stress tests for {contract_address}...\n")

    # We test three different buyer profiles
    scenarios = [
        {"name": "Shrimp (0.01 ETH)", "amount": 0.01},
        {"name": "Shark (0.5 ETH)", "amount": 0.5},
        {"name": "Whale (5.0 ETH)", "amount": 5.0}
    ]

    scenario_results = []
    failed_scenarios = []
    max_buy_tax = 0
    max_sell_tax = 0
    is_honeypot = False

    for sim in scenarios:
        print(f"--- Running {sim['name']} ---")
        
        # Call our existing Web3 engine
        result = simulate_trade(contract_address, eth_buy_amount=sim['amount'])
        
        # Store the specific results
        scenario_results.append({
            "scenario": sim['name'],
            "eth_tested": sim['amount'],
            "status": result.get("status"),
            "buy_tax": result.get("buy_tax", 0),
            "sell_tax": result.get("sell_tax", 0),
            "is_sellable": result.get("is_sellable", True)
        })

        # Track the absolute highest taxes we see across all tests
        if result.get("buy_tax", 0) > max_buy_tax:
            max_buy_tax = result.get("buy_tax", 0)
        if result.get("sell_tax", 0) > max_sell_tax:
            max_sell_tax = result.get("sell_tax", 0)

        # If it fails even ONE scenario, we flag it
        if not result.get("is_sellable", True):
            is_honeypot = True
            failed_scenarios.append(sim['name'])
            print(f"  [!] Honeypot Trap triggered on {sim['name']} size!")
        elif result.get("status") in ["High Risk", "Warning", "Error"]:
            failed_scenarios.append(sim['name'])

    # --- Evaluate the Overall Scenario Risk ---
    print("\n[Scenario Runner] Compiling final report...")
    
    status = "Pass"
    reason = "Passed all trade size scenarios. No dynamic taxes detected."

    if is_honeypot:
        status = "High Risk"
        reason = f"Dynamic Honeypot! The token blocks sells on these trade sizes: {', '.join(failed_scenarios)}"
    elif len(failed_scenarios) > 0:
        status = "Warning"
        reason = f"Failed stress tests on: {', '.join(failed_scenarios)}. Taxes may scale dynamically with trade size."
        
        # If taxes jumped drastically between scenarios.
        # Keep this conservative to avoid false honeypot labels on large-cap tokens.
        if max_buy_tax > 60 or max_sell_tax > 60:
            status = "High Risk"
            reason += f" Extreme dynamic taxes detected (Max Buy: {max_buy_tax:.1f}%, Max Sell: {max_sell_tax:.1f}%)."
        elif max_buy_tax > 20 or max_sell_tax > 20:
            reason += f" Notable dynamic slippage/tax behavior (Max Buy: {max_buy_tax:.1f}%, Max Sell: {max_sell_tax:.1f}%)."

    return {
        "status": status,
        "reason": reason,
        "is_sellable": not is_honeypot,
        "max_buy_tax_detected": round(max_buy_tax, 2),
        "max_sell_tax_detected": round(max_sell_tax, 2),
        "detailed_breakdown": scenario_results
    }

# --- Quick Test Block ---
if __name__ == "__main__":
    # Test our live USDT token again to see it pass all 3 scenarios
    test_target = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    
    final_report = run_stress_tests(test_target)
    
    print(f"\n--- Final Scenario Report ---")
    print(json.dumps(final_report, indent=4))