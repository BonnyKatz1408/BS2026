import json
import os

import honeypot_v1
import minting_v1
import scoring_engine


def _base_detector_output() -> dict:
    return {
        "taxes": {"status": "Skipped", "reason": "Offline local test mode."},
        "liquidity": {"status": "Skipped", "reason": "Offline local test mode."},
        "holders": {"status": "Skipped", "reason": "Offline local test mode."},
        "transactions": {"status": "Skipped", "reason": "Offline local test mode."},
        "age": {"status": "Skipped", "reason": "Offline local test mode.", "age_days": None},
        "rugpull": {"status": "Skipped", "reason": "Offline local test mode."},
    }


def _simulation_from_honeypot(honeypot_result: dict) -> dict:
    if honeypot_result.get("status") == "High Risk":
        return {
            "status": "High Risk",
            "reason": "Local simulation inferred sell-block risk from honeypot detector.",
            "is_sellable": False,
            "max_buy_tax_detected": 0.0,
            "max_sell_tax_detected": 99.0,
            "detailed_breakdown": [],
        }
    return {
        "status": "Pass",
        "reason": "No sell-block inferred in local test mode.",
        "is_sellable": True,
        "max_buy_tax_detected": 0.0,
        "max_sell_tax_detected": 0.0,
        "detailed_breakdown": [],
    }


def run_local_analysis(sol_file: str) -> dict:
    detectors = _base_detector_output()
    detectors["honeypot"] = honeypot_v1.check(sol_file)
    detectors["minting"] = minting_v1.check(sol_file)

    simulation = _simulation_from_honeypot(detectors["honeypot"])
    score = scoring_engine.calculate(detectors, simulation)

    return {
        "contract": sol_file,
        "risk_profile": score,
        "detectors": detectors,
        "simulation": simulation,
    }


if __name__ == "__main__":
    tests = [
        "test_safe_token.sol",
        "test_honeypot_token.sol",
        "test_rugpull_token.sol",
    ]

    final = []
    for file_name in tests:
        if not os.path.exists(file_name):
            final.append({"contract": file_name, "error": "File not found"})
            continue
        final.append(run_local_analysis(file_name))

    print(json.dumps(final, indent=2))

