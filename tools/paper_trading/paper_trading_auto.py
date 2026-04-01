"""
Rule-based paper auto-trading: take-profit / stop-loss exits and optional DCA buys.
Does not predict markets — automates sells at targets and optional recurring buys.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Optional

import paper_trading
import paper_trading_db
import gemini_service


def _position_pl_pct(row: dict) -> Optional[float]:
    """Return live P/L % vs cost for an open position, or None if unpriced."""
    addr = row["token_address"]
    qty = Decimal(str(row["quantity"]))
    cost = Decimal(str(row["cost_eth"]))
    vf = row.get("v3_fee")
    v3_fee = int(vf) if vf is not None else None
    cur = paper_trading.eth_per_token_market(addr, v3_fee=v3_fee)
    if cur is None:
        return None
    value = qty * Decimal(str(cur))
    pl_eth = value - cost
    if cost <= 0:
        return 0.0
    return float((pl_eth / cost) * 100)


def run_auto_tick(username: str) -> dict[str, Any]:
    """
    Evaluate auto-exit rules on all open positions, then optional DCA buy.
    Returns { actions: [...], errors: [...] } (DB updates done inside).
    """
    actions: list[dict[str, Any]] = []
    errors: list[str] = []

    settings = paper_trading_db.get_auto_settings(username)
    if (
        not settings.get("auto_exit_enabled")
        and not settings.get("dca_enabled")
        and not settings.get("ai_trading_enabled")
    ):
        return {"actions": [], "errors": []}

    # --- AI Trading Logic ---
    if settings.get("ai_trading_enabled"):
        positions = paper_trading_db.list_open_positions(username)
        for pos in positions:
            pl_pct = _position_pl_pct(pos)
            if pl_pct is None:
                continue
            
            pid = int(pos["id"])
            addr = pos["token_address"]
            qty = Decimal(str(pos["quantity"]))
            vf = pos.get("v3_fee")
            v3_fee = int(vf) if vf is not None else None

            # Prepare basic context for AI
            token_data = {
                "id": pid,
                "symbol": pos.get("token_symbol"),
                "token_address": addr,
                "pl_pct": round(pl_pct, 4),
                "cost_eth": float(pos.get("cost_eth")),
                "quantity": float(qty),
            }
            
            signal = gemini_service.get_trading_prediction(token_data)
            
            if signal == "SELL":
                proceeds = paper_trading.quote_sell_eth(addr, qty, v3_fee=v3_fee)
                if proceeds is None or proceeds <= 0:
                    errors.append(f"AI-SELL: no sell quote for position {pid}.")
                    continue

                res = paper_trading_db.sell_position(
                    username, pid, Decimal(str(proceeds)), exit_reason="ai_signal"
                )
                if res.get("success"):
                    actions.append(
                        {
                            "type": "sell",
                            "position_id": pid,
                            "reason": "ai_signal",
                            "pl_pct": round(pl_pct, 4),
                            "proceeds_eth": float(proceeds),
                        }
                    )
                else:
                    errors.append(res.get("error_message") or f"AI Sell failed for {pid}.")

    # --- Auto exit (take profit / stop loss) ---
    if settings.get("auto_exit_enabled"):
        tp = settings.get("take_profit_pct")
        sl = settings.get("stop_loss_pct")
        tp_f = float(tp) if tp is not None else None
        sl_f = float(sl) if sl is not None else None

        positions = paper_trading_db.list_open_positions(username)
        for pos in positions:
            pl_pct = _position_pl_pct(pos)
            if pl_pct is None:
                pid = int(pos["id"])
                errors.append(
                    f"Auto-exit skipped position {pid}: no live price (could not quote mark)."
                )
                continue
            pid = int(pos["id"])
            addr = pos["token_address"]
            qty = Decimal(str(pos["quantity"]))
            vf = pos.get("v3_fee")
            v3_fee = int(vf) if vf is not None else None

            reason: Optional[str] = None
            if tp_f is not None and pl_pct >= tp_f:
                reason = "take_profit"
            elif sl_f is not None and pl_pct <= -abs(sl_f):
                reason = "stop_loss"

            if not reason:
                continue

            proceeds = paper_trading.quote_sell_eth(addr, qty, v3_fee=v3_fee)
            if proceeds is None or proceeds <= 0:
                errors.append(f"Auto-{reason}: no sell quote for position {pid}.")
                continue

            res = paper_trading_db.sell_position(
                username, pid, Decimal(str(proceeds)), exit_reason=reason
            )
            if res.get("success"):
                actions.append(
                    {
                        "type": "sell",
                        "position_id": pid,
                        "reason": reason,
                        "pl_pct": round(pl_pct, 4),
                        "proceeds_eth": float(proceeds),
                    }
                )
            else:
                errors.append(res.get("error_message") or f"Sell failed for {pid}.")

    # --- DCA (recurring buy) ---
    if settings.get("dca_enabled"):
        raw = settings.get("dca_token_address")
        eth_amt = settings.get("dca_eth_amount")
        interval = settings.get("dca_interval_minutes")
        if not raw or eth_amt is None or interval is None or float(interval) <= 0:
            errors.append("DCA enabled but token, ETH amount, or interval is incomplete.")
        else:
            try:
                import validator

                token_address = validator.format_address(str(raw).strip())
            except Exception as e:
                errors.append(f"DCA: invalid token address: {e}")
                token_address = None

            if token_address:
                eth_f = float(eth_amt)
                if eth_f <= 0:
                    errors.append("DCA: eth amount must be positive.")
                else:
                    last = settings.get("dca_last_run_at")
                    interval_m = int(interval)
                    now = datetime.utcnow()
                    should_run = False
                    if last is None:
                        should_run = True
                    else:
                        ln = last
                        if getattr(ln, "tzinfo", None) is not None:
                            ln = ln.astimezone(timezone.utc).replace(tzinfo=None)
                        if now >= ln + timedelta(minutes=interval_m):
                            should_run = True

                    if should_run:
                        # AI Check for buy signal if AI trading is enabled
                        if settings.get("ai_trading_enabled"):
                            token_meta = paper_trading.get_token_meta(token_address)
                            buy_context = {
                                "action": "BUY_DCA",
                                "token_address": token_address,
                                "symbol": token_meta.get("symbol"),
                                "eth_amount": eth_f,
                            }
                            signal = gemini_service.get_trading_prediction(buy_context)
                            if signal != "BUY":
                                should_run = False

                    if should_run:
                        qb = paper_trading.quote_buy_paper(token_address, eth_f)
                        if not qb.get("ok"):
                            errors.append(
                                f"DCA buy quote failed: {qb.get('error_message', 'unknown')}"
                            )
                        else:
                            tokens_human = float(qb["tokens_human"])
                            v3_fee_i = (
                                int(qb["v3_fee"]) if qb.get("v3_fee") is not None else None
                            )
                            meta = paper_trading.get_token_meta(token_address)
                            pair = paper_trading.get_pair_address(token_address)
                            qty = Decimal(str(tokens_human))
                            cost_eth = Decimal(str(eth_f))
                            avg_buy = cost_eth / qty if qty > 0 else Decimal(0)
                            sym = meta.get("symbol") or "TOKEN"
                            name = meta.get("name") or ""

                            res = paper_trading_db.buy_position(
                                username=username,
                                token_address=token_address,
                                chain="ethereum",
                                token_symbol=sym,
                                token_name=name or sym,
                                tagline=None,
                                pair_address=pair,
                                v3_fee=v3_fee_i,
                                eth_spent=cost_eth,
                                quantity_tokens=qty,
                                avg_buy_price_eth=avg_buy,
                                cost_eth=cost_eth,
                            )
                            if res.get("success"):
                                paper_trading_db.touch_dca_last_run(username)
                                actions.append(
                                    {
                                        "type": "dca_buy",
                                        "token_address": token_address,
                                        "eth_amount": eth_f,
                                        "position_id": res.get("position_id"),
                                    }
                                )
                            else:
                                errors.append(
                                    res.get("error_message") or "DCA buy failed."
                                )

    return {"actions": actions, "errors": errors}
