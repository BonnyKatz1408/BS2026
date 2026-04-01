import re
import etherscan_client


def _has_pattern(source_code: str, patterns: list[str]) -> bool:
    lower_src = source_code.lower()
    return any(re.search(p, lower_src) for p in patterns)


def check(contract_address: str) -> dict:
    """
    Detects risky owner controls from source code:
    - mint/supply controls
    - blacklist/whitelist controls
    - pause controls
    """
    print(f"[Minting Detector] Scanning contract controls for {contract_address}...")
    if contract_address.endswith(".sol"):
        try:
            with open(contract_address, "r", encoding="utf-8") as f:
                source = f.read()
            code_data = {"status": "Success", "source_code": source}
        except Exception as e:
            code_data = {"status": "Error", "reason": f"Failed to read local source: {str(e)}"}
    else:
        code_data = etherscan_client.fetch_source_code(contract_address)

    if code_data.get("status") != "Success":
        return {
            "status": "Error",
            "reason": f"Cannot analyze source code: {code_data.get('reason', 'Unknown error')}",
            "minting_enabled": None,
            "can_pause_trading": None,
            "has_blacklist_controls": None,
        }

    source = code_data.get("source_code", "")
    if not source:
        return {
            "status": "Error",
            "reason": "Empty source code.",
            "minting_enabled": None,
            "can_pause_trading": None,
            "has_blacklist_controls": None,
        }

    mint_patterns = [
        r"\bfunction\s+mint\b",
        r"\b_mint\s*\(",
        r"\bincrease[s_]?supply\b",
    ]
    burn_patterns = [
        r"\bfunction\s+burn\b",
        r"\b_burn\s*\(",
        r"\bdecrease[s_]?supply\b",
    ]
    pause_patterns = [
        r"\bfunction\s+pause\b",
        r"\bfunction\s+unpause\b",
        r"\bwhennotpaused\b",
        r"\bwhenpaused\b",
    ]
    blacklist_patterns = [
        r"\bblacklist\b",
        r"\bisblacklisted\b",
        r"\bsetblacklist\b",
        r"\bexclude[from_]?trading\b",
    ]
    owner_guard_patterns = [
        r"\bonlyowner\b",
        r"\bowner\s*==\s*msg\.sender\b",
    ]

    has_mint = _has_pattern(source, mint_patterns)
    has_burn = _has_pattern(source, burn_patterns)
    has_pause = _has_pattern(source, pause_patterns)
    has_blacklist = _has_pattern(source, blacklist_patterns)
    has_owner_guard = _has_pattern(source, owner_guard_patterns)

    status = "Pass"
    reasons = []

    if has_mint and has_owner_guard and has_pause:
        status = "High Risk"
        reasons.append("Owner-gated minting with pause controls detected.")
    elif has_mint and has_owner_guard:
        status = "Warning"
        reasons.append("Owner-gated minting detected. Supply could potentially be increased.")
    elif has_mint:
        status = "Warning"
        reasons.append("Minting capability detected in code.")

    if has_pause:
        if status == "Pass":
            status = "Warning"
        reasons.append("Pause controls found. Trading could be temporarily blocked.")

    if has_blacklist:
        if status != "High Risk":
            status = "Warning"
        reasons.append("Blacklist controls found. Certain wallets may be restricted from transfers.")

    if has_burn and status == "Pass":
        reasons.append("Burn-related functions detected (may support supply decrease logic).")

    if not reasons:
        reasons.append("No obvious mint/pause/blacklist controls detected in source.")

    return {
        "status": status,
        "reason": " | ".join(reasons),
        "minting_enabled": has_mint,
        "burning_enabled": has_burn,
        "can_pause_trading": has_pause,
        "has_blacklist_controls": has_blacklist,
        "owner_control_signals": has_owner_guard,
    }

