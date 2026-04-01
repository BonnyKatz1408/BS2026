from web3 import Web3

def is_valid_address(address: str) -> bool:
    """
    Validates if the provided string is a properly formatted Ethereum address.
    Uses Web3.py to ensure it matches the 42-character 0x hexadecimal format.
    """
    if not address:
        return False
        
    # Web3.is_address checks length, hex characters, and the 0x prefix natively
    return Web3.is_address(address)

def format_address(address: str) -> str:
    """
    Safely converts any valid address into its proper 'Checksum' format.
    (Ethereum nodes require addresses to have specific uppercase/lowercase letters).
    """
    if is_valid_address(address):
        return Web3.to_checksum_address(address)
    raise ValueError(f"Cannot format invalid address: {address}")

# --- Quick Test Block ---
if __name__ == "__main__":
    test_good = "0xdAC17F958D2ee523a2206206994597C13D831ec7"
    test_bad = "0xJustSomeRandomTextThatIsLongEnough"
    
    print(f"Testing Good Address: {is_valid_address(test_good)}") # Should be True
    print(f"Testing Bad Address:  {is_valid_address(test_bad)}")  # Should be False