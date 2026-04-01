from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional

# --- INPUT SCHEMAS (What the Frontend sends us) ---

class AnalyzeRequest(BaseModel):
    """
    The exact JSON structure we expect from the frontend when they ask for an audit.
    """
    contract_address: str = Field(
        ..., 
        description="The 42-character Ethereum smart contract address.",
        min_length=42,
        max_length=42
    )
    
    # We use a Pydantic validator to do a basic sanity check before it even 
    # hits our validator.py file. If it fails here, the API instantly rejects it.
    @field_validator('contract_address')
    @classmethod
    def check_hex(cls, v: str) -> str:
        if not v.startswith('0x'):
            raise ValueError("Contract address must start with '0x'")
        return v

# --- OUTPUT SCHEMAS (What we send back to the Frontend) ---

class RiskProfile(BaseModel):
    numeric_score: int
    risk_level: str
    driving_factors: List[str]
    confidence_score: int = 0

class AnalyzeResponse(BaseModel):
    """
    The master blueprint for the JSON response we send back to the user.
    This guarantees the frontend always gets the exact same structure.
    """
    success: bool
    contract_address: str
    
    # We use Optional because if the analysis crashes, we might only send an error message
    risk_profile: Optional[RiskProfile] = None
    
    # Dictionaries to hold the raw output from our detector files
    detectors: Optional[Dict[str, Any]] = None
    simulation: Optional[Dict[str, Any]] = None
    token_metadata: Optional[Dict[str, Any]] = None
    
    # The final Gemini AI English summary
    ai_summary: Optional[str] = None

    # Verified Solidity source from Etherscan (same fetch as analysis gate; for dashboard viewer)
    contract_source: Optional[str] = None

    # Prior scans + gating for optional MySQL-backed history (see scan_history_db.py)
    token_history: Optional[Dict[str, Any]] = None
    
    # If something goes wrong, we populate this
    error_message: Optional[str] = None

# --- Quick Test Block ---
if __name__ == "__main__":
    print("Testing Schema Validation...\n")
    
    try:
        # This should fail perfectly and throw a Pydantic error
        bad_request = AnalyzeRequest(contract_address="JustSomeRandomString")
    except Exception as e:
        print(f"Caught bad request successfully! Error:\n{e}\n")

    # This should pass perfectly
    good_request = AnalyzeRequest(contract_address="0xdAC17F958D2ee523a2206206994597C13D831ec7")
    print(f"Good request validated: {good_request.contract_address}")