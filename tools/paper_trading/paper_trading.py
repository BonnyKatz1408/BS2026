"""
Paper trading: Uniswap V2 + V3 (QuoterV2) quotes on Ethereum mainnet (same RPC as engine).
"""
from __future__ import annotations

from decimal import Decimal, ROUND_DOWN
from typing import Any, Optional

import engine

ROUTER_ABI = engine.ROUTER_ABI

# Uniswap V3 QuoterV2 — Ethereum mainnet (single-hop quotes when V2 has no pool)
QUOTER_V2 = "0x61fFE014bA17989E743c5F6cB21bF9697530B21e"
QUOTER_V2_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "tokenIn", "type": "address"},
                    {"internalType": "address", "name": "tokenOut", "type": "address"},
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"},
                ],
                "internalType": "struct IQuoterV2.QuoteExactInputSingleParams",
                "name": "params",
                "type": "tuple",
            }
        ],
        "name": "quoteExactInputSingle",
        "outputs": [
            {"internalType": "uint256", "name": "amountOut", "type": "uint256"},
            {"internalType": "uint160", "name": "sqrtPriceX96After", "type": "uint160"},
            {"internalType": "uint32", "name": "initializedTicksCrossed", "type": "uint32"},
            {"internalType": "uint256", "name": "gasEstimate", "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]

# Try common fee tiers first (most pools use 0.3% or 1%)
V3_FEE_TIERS = (3000, 500, 10000, 100)

ERC20_EXTRA = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]

FACTORY_ABI = [
    {
        "constant": True,
        "inputs": [
            {"name": "tokenA", "type": "address"},
            {"name": "tokenB", "type": "address"},
        ],
        "name": "getPair",
        "outputs": [{"name": "pair", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]

UNISWAP_V2_FACTORY = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"


def _router():
    w3 = engine.w3
    return w3.eth.contract(
        address=w3.to_checksum_address(engine.UNISWAP_V2_ROUTER),
        abi=ROUTER_ABI,
    )


def _quoter_v3():
    w3 = engine.w3
    return w3.eth.contract(
        address=w3.to_checksum_address(QUOTER_V2),
        abi=QUOTER_V2_ABI,
    )


def _factory():
    w3 = engine.w3
    return w3.eth.contract(
        address=w3.to_checksum_address(UNISWAP_V2_FACTORY),
        abi=FACTORY_ABI,
    )


def get_token_decimals(token_address: str) -> int:
    w3 = engine.w3
    token = w3.eth.contract(
        address=w3.to_checksum_address(token_address),
        abi=engine.ERC20_ABI,
    )
    try:
        d = int(token.functions.decimals().call())
        if 0 <= d <= 36:
            return d
    except Exception:
        pass
    return 18


def get_token_meta(token_address: str) -> dict[str, Any]:
    w3 = engine.w3
    addr = w3.to_checksum_address(token_address)
    abi = engine.ERC20_ABI + ERC20_EXTRA
    token = w3.eth.contract(address=addr, abi=abi)
    name, symbol = "Unknown", "TOKEN"
    try:
        n = token.functions.name().call()
        if isinstance(n, str) and n.strip():
            name = n.strip()[:255]
    except Exception:
        pass
    try:
        s = token.functions.symbol().call()
        if isinstance(s, str) and s.strip():
            symbol = s.strip()[:64]
    except Exception:
        pass
    dec = get_token_decimals(token_address)
    return {"name": name, "symbol": symbol, "decimals": dec}


def get_pair_address(token_address: str) -> Optional[str]:
    w3 = engine.w3
    weth = w3.to_checksum_address(engine.WETH_ADDRESS)
    token = w3.to_checksum_address(token_address)
    fac = _factory()
    try:
        pair = fac.functions.getPair(token, weth).call()
        if pair and int(pair, 16) != 0:
            return w3.to_checksum_address(pair)
    except Exception:
        pass
    return None


def human_tokens_to_wei(amount: Decimal, decimals: int) -> int:
    scale = Decimal(10) ** decimals
    raw = (amount * scale).quantize(Decimal("1"), rounding=ROUND_DOWN)
    if raw < 0:
        return 0
    return int(raw)


def quote_buy_simulation(token_address: str, eth_amount: float) -> dict[str, Any]:
    return engine.simulate_trade(token_address, eth_buy_amount=eth_amount)


def _quote_v3_buy_exact(
    token_address: str, eth_amount: float
) -> Optional[dict[str, Any]]:
    """WETH -> token via QuoterV2; returns tokens_human, fee, decimals or None."""
    w3 = engine.w3
    weth = w3.to_checksum_address(engine.WETH_ADDRESS)
    token = w3.to_checksum_address(token_address)
    amount_in_wei = w3.to_wei(eth_amount, "ether")
    decimals = get_token_decimals(token_address)
    quoter = _quoter_v3()
    for fee in V3_FEE_TIERS:
        try:
            params = (weth, token, amount_in_wei, fee, 0)
            out = quoter.functions.quoteExactInputSingle(params).call()
            amount_out = int(out[0])
            if amount_out > 0:
                return {
                    "tokens_human": float(amount_out) / (10**decimals),
                    "fee": fee,
                    "decimals": decimals,
                }
        except Exception:
            continue
    return None


def _quote_v2_sell_eth(
    token_address: str, token_amount_human: Decimal
) -> Optional[float]:
    if token_amount_human <= 0:
        return 0.0
    w3 = engine.w3
    weth = w3.to_checksum_address(engine.WETH_ADDRESS)
    token = w3.to_checksum_address(token_address)
    dec = get_token_decimals(token_address)
    wei_in = human_tokens_to_wei(token_amount_human, dec)
    if wei_in == 0:
        return 0.0
    router = _router()
    try:
        amounts = router.functions.getAmountsOut(wei_in, [token, weth]).call()
        eth_out = float(w3.from_wei(amounts[1], "ether"))
        return eth_out if eth_out > 0 else None
    except Exception:
        return None


def _quote_v3_sell_exact_fee(
    token_address: str, token_amount_human: Decimal, fee: int
) -> Optional[float]:
    """Token -> WETH for a specific V3 fee tier."""
    if token_amount_human <= 0:
        return 0.0
    w3 = engine.w3
    weth = w3.to_checksum_address(engine.WETH_ADDRESS)
    token = w3.to_checksum_address(token_address)
    dec = get_token_decimals(token_address)
    wei_in = human_tokens_to_wei(token_amount_human, dec)
    if wei_in == 0:
        return 0.0
    quoter = _quoter_v3()
    try:
        params = (token, weth, wei_in, fee, 0)
        out = quoter.functions.quoteExactInputSingle(params).call()
        eth_out = float(w3.from_wei(int(out[0]), "ether"))
        return eth_out if eth_out > 0 else None
    except Exception:
        return None


def _quote_v3_sell_best_fee(token_address: str, token_amount_human: Decimal) -> Optional[float]:
    """Pick best ETH out across fee tiers (when pool tier is unknown)."""
    best: Optional[float] = None
    for fee in V3_FEE_TIERS:
        eth_out = _quote_v3_sell_exact_fee(token_address, token_amount_human, fee)
        if eth_out is not None and (best is None or eth_out > best):
            best = eth_out
    return best


def quote_buy_paper(token_address: str, eth_amount: float) -> dict[str, Any]:
    """
    Buy quote for paper trading: Uniswap V2 first, then V3 QuoterV2.
    Returns: ok, tokens_human, source ('v2'|'v3'), v3_fee (int|None), error_message
    """
    sim = engine.simulate_trade(token_address, eth_buy_amount=eth_amount)
    if sim.get("status") == "Error":
        v3 = _quote_v3_buy_exact(token_address, eth_amount)
        if v3 and v3["tokens_human"] > 0:
            return {
                "ok": True,
                "tokens_human": v3["tokens_human"],
                "source": "v3",
                "v3_fee": v3["fee"],
            }
        return {"ok": False, "error_message": _paper_buy_failure_message(sim, eth_amount)}

    tokens_human = float(
        sim.get("estimated_tokens_received_human")
        or sim.get("expected_tokens_out_human")
        or 0.0
    )
    if tokens_human > 0:
        return {
            "ok": True,
            "tokens_human": tokens_human,
            "source": "v2",
            "v3_fee": None,
        }

    v3 = _quote_v3_buy_exact(token_address, eth_amount)
    if v3 and v3["tokens_human"] > 0:
        return {
            "ok": True,
            "tokens_human": v3["tokens_human"],
            "source": "v3",
            "v3_fee": v3["fee"],
        }

    return {
        "ok": False,
        "error_message": _paper_buy_failure_message(sim, eth_amount),
    }


def _paper_buy_failure_message(sim: dict[str, Any], eth_amount: float) -> str:
    """User-facing explanation when no V2/V3 quote works (incl. honeypot / no pool)."""
    parts: list[str] = []
    st = (sim.get("status") or "").strip()
    det = (sim.get("details") or sim.get("reason") or "").strip()
    if st == "High Risk" and det:
        if "revert" in det.lower() or "honeypot" in det.lower():
            parts.append(
                "The on-chain swap simulation reverted or flagged high risk (often no usable pool or swap restrictions)."
            )
        else:
            parts.append(det[:280] + ("…" if len(det) > 280 else ""))
    elif st == "Error" and det:
        parts.append(det[:280] + ("…" if len(det) > 280 else ""))

    parts.append(
        "No Uniswap V2 or V3 quote worked on Ethereum mainnet for "
        f"~{eth_amount:g} ETH. "
        "This token may have no WETH liquidity here, may be V4-only or traded elsewhere, "
        "or routers cannot complete the path - try a smaller amount or verify the token is on Ethereum."
    )
    return " ".join(parts)


def eth_per_token_market(
    token_address: str, v3_fee: Optional[int] = None
) -> Optional[float]:
    """ETH received when selling 1.0 human-readable token (V2, else V3)."""
    one = Decimal(1)
    return quote_sell_eth(token_address, one, v3_fee=v3_fee)


def quote_sell_eth(
    token_address: str,
    token_amount_human: Decimal,
    v3_fee: Optional[int] = None,
) -> Optional[float]:
    """
    ETH received for selling token_amount_human tokens.
    If v3_fee is set (position was filled via V3), use that tier first; else V2 then V3 best.
    """
    if token_amount_human <= 0:
        return 0.0
    if v3_fee is not None:
        eth = _quote_v3_sell_exact_fee(token_address, token_amount_human, int(v3_fee))
        if eth is not None and eth > 0:
            return eth
    eth_v2 = _quote_v2_sell_eth(token_address, token_amount_human)
    if eth_v2 is not None and eth_v2 > 0:
        return eth_v2
    return _quote_v3_sell_best_fee(token_address, token_amount_human)


def dexscreener_embed_url(chain_slug: str, pair_or_token: str) -> str:
    """Dark embed URL for DexScreener (pair preferred)."""
    addr = pair_or_token.strip().lower()
    if not addr.startswith("0x"):
        addr = "0x" + addr
    base = f"https://dexscreener.com/{chain_slug}/{addr}"
    return f"{base}?embed=1&theme=dark&trades=0&info=0"
