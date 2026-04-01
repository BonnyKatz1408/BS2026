import json
import logging
import os
import re
from contextlib import contextmanager

import google.generativeai as genai
from dotenv import load_dotenv
import etherscan_client

# Load environment variables
load_dotenv()

# Configure Gemini for semantic analysis
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def _compact_reason(text: str, max_chars: int = 260) -> str:
    """Keep detector reasons short and dashboard-friendly."""
    s = (text or "").strip().replace("\n", " ")
    s = re.sub(r"\s+", " ", s)
    if len(s) <= max_chars:
        return s
    return s[: max_chars - 3].rstrip() + "..."


def _contains_sell_block_markers(text: str) -> bool:
    t = (text or "").lower()
    markers = [
        "cannot sell",
        "can't sell",
        "sell blocked",
        "owner-only selling",
        "users cannot transfer",
        "blacklist can block sells",
        "funds are locked",
        "honeypot",
        "transfer revert",
        "blocked transfer",
        "blacklist",
    ]
    return any(m in t for m in markers)


def _mentions_tax_only(text: str) -> bool:
    t = (text or "").lower()
    tax_terms = ["sell tax", "buy tax", "initialselltax", "_initialselltax", "tax"]
    block_terms = ["cannot sell", "blocked", "blacklist", "revert", "owner-only"]
    return any(x in t for x in tax_terms) and not any(x in t for x in block_terms)


@contextmanager
def _slither_quiet_compile():
    """Temporarily silence CryticCompile/solc WARNING lines from arbitrary token sources."""
    crytic = logging.getLogger("CryticCompile")
    slither = logging.getLogger("Slither")
    prev_c, prev_s = crytic.level, slither.level
    crytic.setLevel(logging.ERROR)
    slither.setLevel(logging.ERROR)
    try:
        yield
    finally:
        crytic.setLevel(prev_c)
        slither.setLevel(prev_s)


def check(target: str) -> dict:
    """
    Hybrid Analysis: Uses Slither for deterministic bug finding and 
    Gemini for semantic honeypot/intent detection.
    """
    results = {
        "status": "Pass",
        "reason": "",
        "slither_criticals": [],
        "ai_analysis": ""
    }

    # --- PART 1: SLITHER (Math & Bug Analysis) ---
    try:
        from slither.slither import Slither

        print(f"[Slither Engine] Scanning {target} for bugs...")
        with _slither_quiet_compile():
            if target.endswith(".sol"):
                slither_engine = Slither(target)
            else:
                slither_engine = Slither(f"mainnet:{target}")

        critical_flags = [d.NAME for d in slither_engine.detectors if d.IMPACT == 3]
        results["slither_criticals"] = list(set(critical_flags))

    except Exception as e:
        print(f"[Slither Warning] Could not complete static analysis: {e}")

    # --- PART 2: GEMINI (Intent & Honeypot Analysis) ---
    print(f"[Gemini Engine] Reading source code for malicious intent...")
    try:
        source_code = ""
        if target.endswith(".sol"):
            with open(target, "r", encoding="utf-8") as file:
                source_code = file.read()
        else:
            code_data = etherscan_client.fetch_source_code(target)
            if code_data.get("status") == "Success":
                source_code = code_data.get("source_code", "")

        if source_code and GEMINI_API_KEY:
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = (
                "You are a smart contract auditor. Analyze this Solidity code for honeypot behavior. "
                "Return strict JSON only with keys: verdict, reason. "
                "Allowed verdict values: malicious, benign, uncertain. "
                "A malicious verdict requires concrete evidence that users can buy but cannot sell, "
                "or owner-only transfer/sell controls, blacklist traps, or hidden transfer reverts. "
                "Do NOT classify as malicious from high taxes alone. "
                "Reason must be <= 180 characters and one line. "
                f"Code:\n{source_code}"
            )
            
            ai_response = model.generate_content(prompt)
            ai_text = ai_response.text.strip()
            results["ai_analysis"] = ai_text

            verdict = "uncertain"
            reason = ai_text
            try:
                # Handle both plain JSON and markdown-fenced JSON blocks.
                json_blob = ai_text
                if "```" in ai_text:
                    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", ai_text, re.DOTALL | re.IGNORECASE)
                    if m:
                        json_blob = m.group(1).strip()
                parsed = json.loads(json_blob)
                verdict = str(parsed.get("verdict", "uncertain")).strip().lower()
                reason = str(parsed.get("reason", ai_text)).strip()
                results["ai_analysis"] = reason
            except Exception:
                lowered = ai_text.lower()
                # Conservative fallback: only flag malicious on explicit exploit language.
                malicious_markers = [
                    "cannot sell",
                    "can't sell",
                    "sell blocked",
                    "owner-only selling",
                    "users cannot transfer",
                    "blacklist can block sells",
                    "funds are locked",
                    "is a honeypot",
                ]
                benign_markers = [
                    "benign",
                    "not a honeypot",
                    "no honeypot",
                    "does not contain",
                    "no malicious",
                ]
                if any(mk in lowered for mk in malicious_markers):
                    verdict = "malicious"
                elif any(mk in lowered for mk in benign_markers):
                    verdict = "benign"
                else:
                    verdict = "uncertain"

            src_lower = source_code.lower()
            reason_lower = reason.lower()

            # Hallucination guard: if AI cites exact identifiers absent from source, downgrade.
            cited_identifiers = ["_initialselltax", "_finalselltax", "addbots", "bots"]
            cites_missing_identifier = any(
                ident in reason_lower and ident not in src_lower for ident in cited_identifiers
            )
            if verdict == "malicious" and cites_missing_identifier:
                verdict = "uncertain"
                reason = "AI cited code identifiers not found in source; honeypot evidence not conclusive."

            # Tax-only claims are warning-level unless explicit sell-block evidence exists.
            if verdict == "malicious" and _mentions_tax_only(reason) and not _contains_sell_block_markers(reason):
                verdict = "warning"
                reason = "High tax behavior noted, but no clear hard sell-block mechanism confirmed."

            if verdict == "malicious":
                results["status"] = "High Risk"
                results["reason"] = (
                    "AI semantic analysis found concrete sell/transfer blocking logic. "
                    + _compact_reason(reason)
                )
            elif verdict == "warning":
                results["status"] = "Warning"
                results["reason"] = _compact_reason(reason)
            elif verdict == "uncertain" and not results["reason"]:
                results["status"] = "Warning"
                results["reason"] = "AI analysis could not conclusively classify honeypot behavior."
        else:
            results["ai_analysis"] = "AI analysis skipped (No code or API key)."

    except Exception as e:
         results["ai_analysis"] = f"AI Error: {e}"

    # If Slither caught something but AI didn't, still mark as High Risk
    if not results["reason"] and len(results["slither_criticals"]) > 0:
        results["status"] = "High Risk"
        results["reason"] = "Slither detected critical structural vulnerabilities."
    elif not results["reason"]:
        results["reason"] = "No critical bugs or clear sell-block honeypot logic detected."

    results["reason"] = _compact_reason(results.get("reason", ""))
    results["ai_analysis"] = _compact_reason(results.get("ai_analysis", ""), max_chars=320)

    return results

# --- Quick Test Block ---
if __name__ == "__main__":
    print("Starting Hybrid AI + Slither Analysis...\n")
    
    # Target our local trap contract
    test_target = "test_contract.sol"
    
    result = check(test_target)
    
    print(f"\n--- Final Output ---")
    import json
    print(json.dumps(result, indent=4))