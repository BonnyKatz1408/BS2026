import os
import json
from dotenv import load_dotenv
from http_client import get_json

# Load environment variables
load_dotenv()
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

def fetch_source_code(contract_address: str) -> dict:
    """
    Fetches the verified Solidity source code of a smart contract using Etherscan V2.
    Handles single-file contracts and unpacks multi-file JSON structures.
    """
    print(f"[Etherscan Client] Fetching source code for {contract_address} (V2 API)...")

    if not ETHERSCAN_API_KEY:
        return {"status": "Error", "reason": "ETHERSCAN_API_KEY is missing from .env file."}

    # Updated Etherscan V2 API Endpoint for Source Code
    # We added /v2/ to the URL and injected chainid=1 for Ethereum Mainnet
    url = (
        f"https://api.etherscan.io/v2/api"
        f"?chainid=1"
        f"&module=contract"
        f"&action=getsourcecode"
        f"&address={contract_address}"
        f"&apikey={ETHERSCAN_API_KEY}"
    )

    try:
        data = get_json(url, timeout=25)

        # Etherscan returns status "0" for failures (like invalid API keys)
        if data.get("status") == "0":
            return {
                "status": "Error",
                "reason": f"Etherscan API rejected the request: {data.get('message')} - {data.get('result')}"
            }

        result = data.get("result", [])[0]
        raw_source = result.get("SourceCode", "")

        if not raw_source:
            return {
                "status": "Error",
                "reason": "Contract source code is unverified or empty. Cannot perform AI analysis."
            }

        # --- THE MULTI-FILE UNPACKER ---
        parsed_source = ""
        
        if raw_source.startswith("{{") and raw_source.endswith("}}"):
            # Strip the outer braces and parse the inner JSON
            clean_json_str = raw_source[1:-1]
            try:
                sources_dict = json.loads(clean_json_str).get("sources", {})
                for file_path, file_content in sources_dict.items():
                    parsed_source += f"\n\n// File: {file_path}\n"
                    parsed_source += file_content.get("content", "")
            except json.JSONDecodeError:
                parsed_source = raw_source # Fallback if parsing fails
        else:
            # It's a standard single-file contract
            parsed_source = raw_source

        print(f"  -> Successfully retrieved {len(parsed_source)} characters of Solidity code.")

        return {
            "status": "Success",
            "contract_name": result.get("ContractName", "Unknown"),
            "compiler_version": result.get("CompilerVersion", "Unknown"),
            "source_code": parsed_source
        }

    except Exception as e:
        return {"status": "Error", "reason": f"Failed to connect to Etherscan: {str(e)}"}

# --- Quick Test Block ---
if __name__ == "__main__":
    # Testing the PEPE token contract
    test_target = "0x6982508145454Ce325dDbE47a25d4ec3d2311933"
    
    result = fetch_source_code(test_target)
    
    if result["status"] == "Success":
        print(f"\nContract Name: {result['contract_name']}")
        print(f"Compiler: {result['compiler_version']}")
        print(f"Code Preview:\n{result['source_code'][:500]}...\n")
    else:
        print(f"\n[!] Fetch Failed: {result['reason']}")