import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
from pydantic import ValidationError

_BASE_DIR = str(Path(__file__).resolve().parent)
# Always load project .env (not CWD) so MySQL password is set when Flask is started from any folder.
load_dotenv(Path(_BASE_DIR) / ".env")
_TEMPLATE_DIR = os.path.join(_BASE_DIR, "templates")
_STATIC_DIR = os.path.join(_BASE_DIR, "static")

# Add detectors, utils, core, and tools to Python path
sys.path.insert(0, os.path.join(_BASE_DIR, "detectors"))
sys.path.insert(0, os.path.join(_BASE_DIR, "utils"))
sys.path.insert(0, os.path.join(_BASE_DIR, "tools"))
sys.path.insert(0, os.path.join(_BASE_DIR, "core"))

from schemas import AnalyzeRequest, AnalyzeResponse, RiskProfile
import validator
import etherscan_client
import scoring_engine
import gemini_service
import honeypot_v1
import liquidity_v1
import holder_v1
import transaction_v1
import tax_calc
import scenarios
import age_v1
import minting_v1
import rugpull_v1
import engine
import liquidity_history_v1
import scan_history_db
# Paper trading modules (now in tools/paper_trading/)
sys.path.insert(0, os.path.join(_BASE_DIR, "tools", "paper_trading"))
import paper_trading
import paper_trading_db
import paper_trading_auto
sys.path.pop(0)
import auth_web

app = Flask(
    __name__,
    template_folder=_TEMPLATE_DIR if os.path.isdir(_TEMPLATE_DIR) else "templates",
    static_folder=_STATIC_DIR if os.path.isdir(_STATIC_DIR) else "static",
    static_url_path="/static",
)
app.secret_key = os.getenv("SECRET_KEY", "change-me-in-production-SECRET_KEY")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=14)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Enable CORS for all API endpoints
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

auth_web.register_auth_routes(app)


def _auth_required_json():
    if "user" not in session:
        return (
            jsonify(
                {
                    "success": False,
                    "error_message": "Authentication required. Please sign in.",
                }
            ),
            401,
        )
    return None


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "success": True,
        "status": "ok",
        "service": "BlockSentinel API Engine"
    }), 200


@app.route('/test-public-api', methods=['GET'])
def test_public():
    """Test endpoint - no auth required"""
    return jsonify({"message": "This is a public test endpoint"}), 200


@app.route('/api/v1/simulate', methods=['POST'])
def simulate_trade_preview():
    """
    User-facing simulation endpoint for the dashboard tool.
    Accepts:
    - contract_address (required)
    - eth_amount (optional, default 1.0)
    - claimed_tokens (optional, user-claimed quote for comparison)
    """
    # Public API - no authentication required for simulation
    try:
        if not request.is_json:
            return jsonify({"success": False, "error_message": "Request body must be JSON."}), 400
        payload = request.get_json(silent=True) or {}
        raw_addr = payload.get("contract_address", "")
        target_address = validator.format_address(raw_addr)
        eth_amount = float(payload.get("eth_amount", 1.0))
        if eth_amount <= 0:
            return jsonify({"success": False, "error_message": "eth_amount must be > 0"}), 400
        claimed_tokens = payload.get("claimed_tokens", None)
        claimed_tokens = float(claimed_tokens) if claimed_tokens is not None and str(claimed_tokens).strip() != "" else None
    except Exception as e:
        return jsonify({"success": False, "error_message": f"Invalid simulation input: {str(e)}"}), 400

    sim = engine.simulate_trade(target_address, eth_buy_amount=eth_amount)
    if sim.get("status") == "Error":
        return jsonify({
            "success": False,
            "contract_address": target_address,
            "error_message": sim.get("details") or sim.get("reason") or "Simulation failed."
        }), 400

    expected_tokens = float(sim.get("expected_tokens_out_human", 0.0) or 0.0)
    delta_tokens = None
    slippage_vs_claim_pct = None
    if claimed_tokens and claimed_tokens > 0:
        delta_tokens = expected_tokens - claimed_tokens
        slippage_vs_claim_pct = (delta_tokens / claimed_tokens) * 100

    return jsonify({
        "success": True,
        "contract_address": target_address,
        "input": {
            "eth_amount": eth_amount,
            "claimed_tokens": claimed_tokens,
        },
        "simulation": sim,
        "comparison": {
            "expected_tokens_from_quote": expected_tokens,
            "delta_tokens_vs_claim": delta_tokens,
            "delta_pct_vs_claim": slippage_vs_claim_pct,
        }
    }), 200


def _paper_disabled_response():
    return (
        jsonify(
            {
                "success": False,
                "database_enabled": False,
                "explain": "Paper trading requires MySQL and PAPER_TRADING_ENABLED (or SCAN_HISTORY_ENABLED) plus MYSQL_* in the environment.",
            }
        ),
        200,
    )


def _paper_enrich_positions(username: str) -> dict:
    """Balance + open positions with live quotes + closed history."""
    from decimal import Decimal

    bal = paper_trading_db.get_balance(username)
    open_rows = paper_trading_db.list_open_positions(username)
    closed_rows = paper_trading_db.list_closed_positions(username, limit=50)
    positions_out = []
    for r in open_rows:
        addr = r["token_address"]
        qty = Decimal(str(r["quantity"]))
        cost = Decimal(str(r["cost_eth"]))
        fee = r.get("v3_fee")
        v3_fee = int(fee) if fee is not None else None
        cur_px = paper_trading.eth_per_token_market(addr, v3_fee=v3_fee)
        current_price_eth = float(cur_px) if cur_px is not None else None
        if cur_px is not None:
            value = qty * Decimal(str(cur_px))
            pl_eth = value - cost
            pl_pct = float((pl_eth / cost) * 100) if cost > 0 else 0.0
            pl_eth_f = float(pl_eth)
        else:
            pl_eth_f = None
            pl_pct = None
        pair = r.get("pair_address") or paper_trading.get_pair_address(addr)
        chart_url = paper_trading.dexscreener_embed_url(
            "ethereum", pair if pair else addr
        )
        purchased = r.get("purchased_at")
        if hasattr(purchased, "strftime"):
            purchased_s = purchased.strftime("%Y-%m-%d %H:%M")
        else:
            purchased_s = str(purchased)[:19].replace("T", " ")
        positions_out.append(
            {
                "id": r["id"],
                "token_address": addr,
                "chain": r.get("chain") or "ethereum",
                "token_symbol": r.get("token_symbol") or "",
                "token_name": r.get("token_name") or "",
                "tagline": r.get("tagline") or "",
                "quantity": float(qty),
                "cost_eth": float(cost),
                "avg_buy_price_eth": float(Decimal(str(r["avg_buy_price_eth"]))),
                "purchased_at": purchased_s,
                "current_price_eth": current_price_eth,
                "pl_eth": pl_eth_f,
                "pl_pct": pl_pct,
                "pair_address": pair,
                "dexscreener_embed_url": chart_url,
            }
        )
    history_out = []
    for h in closed_rows:
        ca = h.get("closed_at")
        if hasattr(ca, "strftime"):
            closed_s = ca.strftime("%Y-%m-%d %H:%M")
        else:
            closed_s = str(ca)[:19].replace("T", " ") if ca else ""
        pa = h.get("purchased_at")
        if hasattr(pa, "strftime"):
            purchased_s = pa.strftime("%Y-%m-%d %H:%M")
        else:
            purchased_s = str(pa)[:19].replace("T", " ") if pa else ""
        cost = float(Decimal(str(h["cost_eth"])))
        sold = h.get("sell_proceeds_eth")
        sold_f = float(Decimal(str(sold))) if sold is not None else None
        pl = (sold_f - cost) if sold_f is not None else None
        history_out.append(
            {
                "id": h["id"],
                "token_address": h["token_address"],
                "token_symbol": h.get("token_symbol") or "",
                "token_name": h.get("token_name") or "",
                "quantity": float(Decimal(str(h["quantity"]))),
                "cost_eth": cost,
                "sell_proceeds_eth": sold_f,
                "pl_eth": pl,
                "exit_reason": h.get("exit_reason") or "",
                "purchased_at": purchased_s,
                "closed_at": closed_s,
            }
        )
    auto_s = paper_trading_db.get_auto_settings(username)
    return {
        "success": True,
        "database_enabled": True,
        "balance_eth": float(bal),
        "positions": positions_out,
        "history": history_out,
        "auto_settings": auto_s,
    }


@app.route("/api/v1/paper-trading", methods=["GET"])
def paper_trading_state():
    denied = _auth_required_json()
    if denied:
        return denied
    if not paper_trading_db.is_enabled():
        return _paper_disabled_response()
    user = session.get("user")
    if not user:
        return _auth_required_json()
    try:
        auto = paper_trading_db.get_auto_settings(user)
        tick_out = None
        if auto.get("auto_exit_enabled") or auto.get("dca_enabled"):
            tick_out = paper_trading_auto.run_auto_tick(user)
        payload = _paper_enrich_positions(user)
        if tick_out is not None:
            payload["auto_tick"] = {
                "actions": tick_out.get("actions") or [],
                "errors": tick_out.get("errors") or [],
            }
        return jsonify(payload), 200
    except Exception as e:
        return jsonify({"success": False, "error_message": str(e)}), 500


@app.route("/api/v1/paper-trading/buy", methods=["POST"])
def paper_trading_buy():
    denied = _auth_required_json()
    if denied:
        return denied
    if not paper_trading_db.is_enabled():
        return _paper_disabled_response()
    user = session.get("user")
    if not request.is_json:
        return jsonify({"success": False, "error_message": "JSON body required."}), 400
    payload = request.get_json(silent=True) or {}
    try:
        raw_addr = payload.get("token_address", "")
        token_address = validator.format_address(raw_addr)
        eth_amount = float(payload.get("eth_amount", 0))
    except Exception as e:
        return jsonify({"success": False, "error_message": f"Invalid input: {e}"}), 400
    if eth_amount <= 0:
        return jsonify({"success": False, "error_message": "eth_amount must be > 0."}), 400

    qb = paper_trading.quote_buy_paper(token_address, eth_amount)
    if not qb.get("ok"):
        return jsonify(
            {
                "success": False,
                "error_message": qb.get("error_message") or "Quote failed.",
            }
        ), 400

    from decimal import Decimal

    tokens_human = float(qb["tokens_human"])
    v3_fee = qb.get("v3_fee")
    v3_fee_i = int(v3_fee) if v3_fee is not None else None

    meta = paper_trading.get_token_meta(token_address)
    pair = paper_trading.get_pair_address(token_address)
    qty = Decimal(str(tokens_human))
    cost_eth = Decimal(str(eth_amount))
    avg_buy = cost_eth / qty
    sym = meta.get("symbol") or "TOKEN"
    name = meta.get("name") or ""

    res = paper_trading_db.buy_position(
        username=user,
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
    if not res.get("success"):
        return jsonify({"success": False, "error_message": res.get("error_message", "Buy failed.")}), 400
    return jsonify({**res, "success": True, "paper": _paper_enrich_positions(user)}), 200


@app.route("/api/v1/paper-trading/top-up", methods=["POST"])
def paper_trading_top_up():
    denied = _auth_required_json()
    if denied:
        return denied
    if not paper_trading_db.is_enabled():
        return _paper_disabled_response()
    user = session.get("user")
    if not request.is_json:
        return jsonify({"success": False, "error_message": "JSON body required."}), 400
    payload = request.get_json(silent=True) or {}
    try:
        from decimal import Decimal

        eth_amount = float(payload.get("eth_amount", 10.0))
    except Exception:
        return jsonify({"success": False, "error_message": "Invalid eth_amount."}), 400
    if eth_amount <= 0 or eth_amount > 1000:
        return jsonify(
            {
                "success": False,
                "error_message": "eth_amount must be between 0 and 1000 (paper ETH).",
            }
        ), 400

    res = paper_trading_db.add_balance(user, Decimal(str(eth_amount)))
    if not res.get("success"):
        return jsonify({"success": False, "error_message": res.get("error_message", "Top-up failed.")}), 400
    return jsonify({**res, "success": True, "paper": _paper_enrich_positions(user)}), 200


@app.route("/api/v1/paper-trading/sell", methods=["POST"])
def paper_trading_sell():
    denied = _auth_required_json()
    if denied:
        return denied
    if not paper_trading_db.is_enabled():
        return _paper_disabled_response()
    user = session.get("user")
    if not request.is_json:
        return jsonify({"success": False, "error_message": "JSON body required."}), 400
    payload = request.get_json(silent=True) or {}
    try:
        position_id = int(payload.get("position_id", 0))
    except Exception:
        position_id = 0
    if position_id <= 0:
        return jsonify({"success": False, "error_message": "position_id required."}), 400

    from decimal import Decimal

    row = paper_trading_db.get_open_position(user, position_id)
    if not row:
        return jsonify({"success": False, "error_message": "Open position not found."}), 404

    addr = row["token_address"]
    qty = Decimal(str(row["quantity"]))
    vf = row.get("v3_fee")
    v3_fee = int(vf) if vf is not None else None
    proceeds = paper_trading.quote_sell_eth(addr, qty, v3_fee=v3_fee)
    if proceeds is None:
        return jsonify(
            {
                "success": False,
                "error_message": "Could not quote a sell on-chain (no route or RPC error).",
            }
        ), 400

    res = paper_trading_db.sell_position(
        user, position_id, Decimal(str(proceeds)), exit_reason="manual"
    )
    if not res.get("success"):
        return jsonify({"success": False, "error_message": res.get("error_message", "Sell failed.")}), 400
    return jsonify({**res, "success": True, "paper": _paper_enrich_positions(user)}), 200


@app.route("/api/v1/paper-trading/auto-settings", methods=["POST"])
def paper_trading_auto_settings():
    denied = _auth_required_json()
    if denied:
        return denied
    if not paper_trading_db.is_enabled():
        return _paper_disabled_response()
    user = session.get("user")
    if not request.is_json:
        return jsonify({"success": False, "error_message": "JSON body required."}), 400
    payload = request.get_json(silent=True) or {}

    from decimal import Decimal

    auto_exit = bool(payload.get("auto_exit_enabled", False))
    tp = payload.get("take_profit_pct")
    sl = payload.get("stop_loss_pct")
    tp_f = float(tp) if tp is not None and str(tp).strip() != "" else None
    sl_f = float(sl) if sl is not None and str(sl).strip() != "" else None
    if tp_f is not None and (tp_f <= 0 or tp_f > 10000):
        return jsonify({"success": False, "error_message": "take_profit_pct out of range."}), 400
    if sl_f is not None and (sl_f <= 0 or sl_f > 100):
        return jsonify({"success": False, "error_message": "stop_loss_pct out of range (use 0–100)."}), 400

    ai_trading = bool(payload.get("ai_trading_enabled", False))

    dca_en = bool(payload.get("dca_enabled", False))
    dca_raw = (payload.get("dca_token_address") or "").strip()
    dca_token = None
    if dca_raw:
        try:
            dca_token = validator.format_address(dca_raw)
        except Exception as e:
            return jsonify({"success": False, "error_message": f"DCA token: {e}"}), 400
    dca_eth = payload.get("dca_eth_amount")
    dca_eth_d = None
    if dca_eth is not None and str(dca_eth).strip() != "":
        try:
            dca_eth_d = Decimal(str(float(dca_eth)))
        except Exception:
            return jsonify({"success": False, "error_message": "Invalid dca_eth_amount."}), 400
        if dca_eth_d <= 0 or dca_eth_d > Decimal("1000"):
            return jsonify({"success": False, "error_message": "DCA ETH amount invalid."}), 400

    dca_iv = payload.get("dca_interval_minutes")
    dca_im = None
    if dca_iv is not None and str(dca_iv).strip() != "":
        try:
            dca_im = int(dca_iv)
        except Exception:
            return jsonify({"success": False, "error_message": "Invalid dca_interval_minutes."}), 400
        if dca_im < 1 or dca_im > 10080:
            return jsonify(
                {"success": False, "error_message": "DCA interval must be 1–10080 minutes."}
            ), 400

    if dca_en and (not dca_token or dca_eth_d is None or dca_im is None):
        return jsonify(
            {
                "success": False,
                "error_message": "DCA requires token address, ETH amount, and interval (minutes).",
            }
        ), 400

    res = paper_trading_db.upsert_auto_settings(
        user,
        auto_exit,
        tp_f,
        sl_f,
        ai_trading,
        dca_en,
        dca_token,
        dca_eth_d,
        dca_im,
    )
    if not res.get("success"):
        return jsonify({"success": False, "error_message": res.get("error_message", "Save failed.")}), 400
    return jsonify({"success": True, "paper": _paper_enrich_positions(user)}), 200


@app.route("/api/v1/paper-trading/auto-tick", methods=["POST"])
def paper_trading_auto_tick():
    denied = _auth_required_json()
    if denied:
        return denied
    if not paper_trading_db.is_enabled():
        return _paper_disabled_response()
    user = session.get("user")
    try:
        out = paper_trading_auto.run_auto_tick(user)
        return jsonify(
            {
                "success": True,
                "actions": out.get("actions") or [],
                "errors": out.get("errors") or [],
                "paper": _paper_enrich_positions(user),
            }
        ), 200
    except Exception as e:
        return jsonify({"success": False, "error_message": str(e)}), 500


@app.route('/api/v1/liquidity-history', methods=['POST'])
def liquidity_history():
    """
    Returns a historical liquidity series for the dashboard liquidity tracker graph.

    Output:
    {
      success: bool,
      contract_address: str,
      pair_address: str|null,
      data: { labels: [...], liquidity_eth: [...] } | null
    }
    """
    denied = _auth_required_json()
    if denied:
        return denied
    try:
        if not request.is_json:
            return jsonify({"success": False, "error_message": "Request body must be JSON."}), 400
        payload = request.get_json(silent=True) or {}
        raw_addr = payload.get("contract_address", "")
        target_address = validator.format_address(raw_addr)
    except Exception as e:
        return jsonify({"success": False, "error_message": f"Invalid input: {str(e)}"}), 400

    # Keep defaults aligned with a lightweight UI chart.
    try:
        points = int(payload.get("points", 24))
    except Exception:
        points = 24
    try:
        window_hours = float(payload.get("window_hours", 12.0))
    except Exception:
        window_hours = 12.0

    series = liquidity_history_v1.get_liquidity_series(
        target_address,
        points=points,
        window_hours=window_hours,
    )
    if series.get("status") != "Success":
        return jsonify({
            "success": False,
            "contract_address": target_address,
            "error_message": series.get("reason", "Failed to fetch liquidity series."),
        }), 400

    return jsonify({
        "success": True,
        "contract_address": target_address,
        "pair_address": series.get("pair_address"),
        "data": {
            "labels": series.get("labels", []),
            "liquidity_eth": series.get("liquidity_eth", []),
            "window_hours": series.get("window_hours"),
            "points": series.get("points"),
        }
    }), 200


@app.route("/api/v1/token-history", methods=["GET"])
def token_history_endpoint():
    """
    Return stored scan snapshots for a contract (newest first).
    """
    denied = _auth_required_json()
    if denied:
        return denied
    try:
        raw_addr = request.args.get("contract_address", "").strip()
        target_address = validator.format_address(raw_addr)
    except Exception as e:
        return jsonify({"success": False, "error_message": f"Invalid address: {str(e)}"}), 400

    if not scan_history_db.is_enabled():
        return jsonify({
            "success": True,
            "database_enabled": False,
            "contract_address": target_address,
            "count": 0,
            "snapshots": [],
            "explain": "The API is not configured with MySQL scan history (SCAN_HISTORY_ENABLED / MYSQL_*).",
        }), 200

    snapshots = scan_history_db.fetch_history(target_address, limit=50)
    return jsonify({
        "success": True,
        "database_enabled": True,
        "contract_address": target_address,
        "count": len(snapshots),
        "snapshots": snapshots,
        "explain": (
            "Each row is a point-in-time snapshot from a completed analyze run on this server. "
            "Compare scores and detector statuses over time to spot rehabilitation, relaunches, "
            "or changing liquidity / tax conditions."
        ),
    }), 200


@app.route("/report-template.html", methods=["GET"])
def report_template_html():
    """Static HTML report shell; dashboard fills {{PLACEHOLDERS}} client-side."""
    path = Path(_BASE_DIR) / "templates" / "Report.html"
    if not path.is_file():
        return jsonify({"success": False, "error_message": "Report.html not found in templates folder."}), 404
    return send_file(path, mimetype="text/html; charset=utf-8")


def _token_history_payload(target_address: str, risk_profile: RiskProfile) -> dict:
    """Load prior snapshots and classify if the main dashboard should surface a history warning."""
    if not scan_history_db.is_enabled():
        return {
            "database_enabled": False,
            "prior_scan_count": 0,
            "surface_main_warning": False,
            "warning_title": None,
            "warning_detail": None,
            "how_we_decided": (
                "Scan history is off. Set SCAN_HISTORY_ENABLED=1 and MYSQL_* in the environment, "
                "then restart the API to retain and compare past scans."
            ),
            "historical_worst_score": None,
            "historical_worst_at": None,
        }
    prior_rows = scan_history_db.fetch_history(target_address, limit=80)
    return scan_history_db.build_history_context_for_response(
        prior_rows,
        int(risk_profile.numeric_score),
        str(risk_profile.risk_level or ""),
    )


def _compute_category_risks(detectors_output: dict, simulation_output: dict) -> dict:
    """
    Build category risk scores required by the frontend:
    1) ownership risk
    2) liquidity risk
    3) transaction risk
    4) contract risk
    5) market behaviour risk
    """
    ownership = 5
    holders = detectors_output.get("holders", {})
    if holders.get("status") == "High Risk":
        ownership = 90
    elif holders.get("status") == "Warning":
        ownership = 60
    elif holders.get("status") == "Error":
        ownership = 35

    liquidity = 5
    liq = detectors_output.get("liquidity", {})
    rugpull = detectors_output.get("rugpull", {})
    if liq.get("status") == "High Risk":
        liquidity = 90
    elif liq.get("status") == "Warning":
        liquidity = 60
    elif liq.get("status") == "Error":
        liquidity = 35
    if rugpull.get("status") == "High Risk":
        liquidity = max(liquidity, 90)
    elif rugpull.get("status") == "Warning":
        liquidity = max(liquidity, 60)
    elif rugpull.get("status") == "Error":
        liquidity = max(liquidity, 35)

    transaction = 5
    tx = detectors_output.get("transactions", {})
    if tx.get("status") == "High Risk":
        transaction = 90
    elif tx.get("status") == "Warning":
        transaction = 60
    elif tx.get("status") == "Error":
        transaction = 35

    contract = 5
    honeypot = detectors_output.get("honeypot", {})
    taxes = detectors_output.get("taxes", {})
    minting = detectors_output.get("minting", {})
    if (
        honeypot.get("status") == "High Risk"
        or taxes.get("status") == "High Risk"
        or minting.get("status") == "High Risk"
    ):
        contract = 95
    elif (
        honeypot.get("status") == "Warning"
        or taxes.get("status") == "Warning"
        or minting.get("status") == "Warning"
    ):
        contract = 65
    elif (
        honeypot.get("status") == "Error"
        or taxes.get("status") == "Error"
        or minting.get("status") == "Error"
    ):
        contract = 40

    market_behaviour = 5
    sim_status = simulation_output.get("status")
    age = detectors_output.get("age", {})
    if sim_status == "High Risk":
        market_behaviour = 90
    elif sim_status == "Warning":
        market_behaviour = 60
    elif sim_status == "Error":
        market_behaviour = 35
    else:
        # Also consider transaction detector because buy/sell imbalance is market behavior.
        if tx.get("status") == "High Risk":
            market_behaviour = max(market_behaviour, 80)
        elif tx.get("status") == "Warning":
            market_behaviour = max(market_behaviour, 55)
    if age.get("status") == "High Risk":
        market_behaviour = max(market_behaviour, 70)
    elif age.get("status") == "Warning":
        market_behaviour = max(market_behaviour, 45)

    # Honeypot-specific category: separate from generic contract risk so UI does not
    # mislabel contract-control risk as a honeypot.
    honeypot_risk = 10
    if honeypot.get("status") == "High Risk":
        honeypot_risk = 80 if sim_status == "High Risk" or simulation_output.get("is_sellable") is False else 35
    elif honeypot.get("status") == "Warning":
        honeypot_risk = 45
    elif honeypot.get("status") == "Error":
        honeypot_risk = 30
    if sim_status == "High Risk" or simulation_output.get("is_sellable") is False:
        honeypot_risk = max(honeypot_risk, 85)
    elif sim_status == "Warning":
        honeypot_risk = max(honeypot_risk, 40)

    return {
        "ownership_risk": ownership,
        "liquidity_risk": liquidity,
        "transaction_risk": transaction,
        "contract_risk": contract,
        "market_behaviour_risk": market_behaviour,
        "honeypot_risk": honeypot_risk,
    }


def _compute_confidence_score(detectors_output: dict, simulation_output: dict) -> int:
    """
    Confidence reflects data completeness and detector health (0-100).
    - Pass/Warning/High Risk => high confidence signals
    - Skipped => partial confidence
    - Error/unknown => low confidence
    """
    items = list(detectors_output.values())
    if simulation_output:
        items.append(simulation_output)
    if not items:
        return 0

    score_total = 0
    for item in items:
        status = str(item.get("status", "")).strip().lower()
        if status in {"pass", "warning", "high risk"}:
            score_total += 100
        elif status == "skipped":
            score_total += 55
        elif status == "error":
            score_total += 20
        else:
            score_total += 40

    return int(round(score_total / len(items)))


def _parse_target_address():
    if not request.is_json:
        raise ValueError("Request body must be JSON.")
    payload = request.get_json(silent=True) or {}
    req_data = AnalyzeRequest(**payload)
    addr = validator.format_address(req_data.contract_address)
    force_refresh = bool(payload.get("force_refresh"))
    return addr, force_refresh


def _finalize_cached_analysis_response(target_address: str, cached: dict, scanned_at) -> dict:
    """Merge fresh token_history into a stored full response; mark cache metadata."""
    out = dict(cached)
    rp_raw = out.get("risk_profile") or {}
    rp = RiskProfile.model_validate(rp_raw)
    out["token_history"] = _token_history_payload(target_address, rp)
    out["response_cached"] = True
    if isinstance(scanned_at, datetime):
        out["cached_at"] = scanned_at.isoformat()
    else:
        out["cached_at"] = str(scanned_at) if scanned_at is not None else None
    return out


def _safe_run(name: str, fn, target_address: str) -> dict:
    try:
        result = fn(target_address)
        if isinstance(result, dict):
            return result
        return {"status": "Error", "reason": f"{name} returned non-dict output."}
    except Exception as e:
        return {"status": "Error", "reason": f"{name} crashed: {str(e)}"}


def _contract_source_for_response(code_data: dict) -> str:
    """Verified Solidity source for the dashboard viewer (same Etherscan payload as the analysis gate)."""
    if code_data.get("status") != "Success":
        return ""
    src = code_data.get("source_code") or ""
    max_len = 450_000
    if len(src) > max_len:
        return src[:max_len] + "\n\n// [Truncated: response size limit]"
    return src


def _enrich_age_growth(detectors_output: dict) -> None:
    """
    Contextualize age with growth/activity so we don't use age as an isolated flag.
    age_growth_ratio combines:
    - liquidity depth (ETH)
    - holder base size
    - transaction turnover
    normalized by token age.
    """
    age_obj = detectors_output.get("age", {})
    if not isinstance(age_obj, dict):
        return
    age_days = age_obj.get("age_days")
    if age_days is None:
        return

    try:
        age_days = max(1, int(age_days))
        liq_eth = float((detectors_output.get("liquidity", {}) or {}).get("eth_in_pool") or 0.0)
        tx_metrics = (detectors_output.get("transactions", {}) or {}).get("metrics", {}) or {}
        turnover = float(tx_metrics.get("turnover_ratio") or 0.0)
        holders_total = int((detectors_output.get("holders", {}) or {}).get("total_holders") or 0)
    except Exception:
        return

    growth_score = liq_eth + (holders_total / 1000.0) + (turnover * 10.0)
    ratio = growth_score / age_days
    age_obj["age_growth_ratio"] = round(ratio, 4)

    # Young + extreme growth often signals speculative/manipulative behavior.
    if age_days <= 14 and ratio >= 25:
        age_obj["status"] = "High Risk"
        age_obj["reason"] = (
            f"Age-growth mismatch: {age_days}d old with outsized growth/activity "
            f"(ratio {ratio:.2f}). Elevated pump/dump risk."
        )
    elif age_days <= 30 and ratio >= 12 and age_obj.get("status") != "High Risk":
        age_obj["status"] = "Warning"
        age_obj["reason"] = (
            f"Fast growth vs age ({age_days}d, ratio {ratio:.2f}). "
            "Monitor volatility and concentration closely."
        )


def _fetch_token_metadata(target_address: str, code_data: dict) -> dict:
    """
    Fetch basic ERC20 metadata for dashboard token info.
    Fails gracefully and returns N/A fields.
    """
    meta = {
        "name": "Unknown",
        "symbol": "N/A",
        "decimals": "N/A",
        "total_supply": "N/A",
        "chain": "ethereum",
    }
    try:
        w3 = engine.w3
        token = w3.eth.contract(
            address=w3.to_checksum_address(target_address),
            abi=[
                {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "payable": False, "stateMutability": "view", "type": "function"},
                {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "payable": False, "stateMutability": "view", "type": "function"},
                {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "payable": False, "stateMutability": "view", "type": "function"},
                {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "payable": False, "stateMutability": "view", "type": "function"},
            ],
        )
        try:
            name = token.functions.name().call()
            if isinstance(name, str) and name.strip():
                meta["name"] = name.strip()
        except Exception:
            pass
        try:
            symbol = token.functions.symbol().call()
            if isinstance(symbol, str) and symbol.strip():
                meta["symbol"] = symbol.strip()
        except Exception:
            pass
        decimals = None
        try:
            decimals = int(token.functions.decimals().call())
            if 0 <= decimals <= 36:
                meta["decimals"] = decimals
        except Exception:
            pass
        try:
            total_supply_raw = int(token.functions.totalSupply().call())
            if decimals is None:
                meta["total_supply"] = str(total_supply_raw)
            else:
                total_supply_h = total_supply_raw / (10 ** decimals)
                meta["total_supply"] = f"{total_supply_h:,.4f}".rstrip("0").rstrip(".")
        except Exception:
            pass
    except Exception:
        pass

    # GoPlus fallback when RPC skips decimals/supply (non-standard ABI or rate limits).
    if meta.get("decimals") == "N/A" or meta.get("total_supply") == "N/A":
        try:
            gp = tax_calc.fetch_goplus_token(target_address)
            if gp:
                dec_guess = None
                for key in ("token_decimal", "decimals"):
                    raw = gp.get(key)
                    if raw is not None and str(raw).strip():
                        try:
                            dec_guess = int(float(str(raw)))
                            if 0 <= dec_guess <= 36:
                                break
                        except (TypeError, ValueError):
                            dec_guess = None
                if meta.get("decimals") == "N/A" and dec_guess is not None:
                    meta["decimals"] = dec_guess
                ts_raw = gp.get("total_supply")
                if meta.get("total_supply") == "N/A" and ts_raw is not None and str(ts_raw).strip():
                    try:
                        raw_int = int(float(str(ts_raw).replace(",", "").split(".")[0]))
                        d = meta["decimals"] if isinstance(meta.get("decimals"), int) else dec_guess
                        if isinstance(d, int) and d >= 0:
                            meta["total_supply"] = (
                                f"{raw_int / (10 ** d):,.4f}".rstrip("0").rstrip(".")
                            )
                    except (TypeError, ValueError, OverflowError):
                        pass
        except Exception:
            pass

    # Fallback contract name from Etherscan if token name call failed.
    if (meta.get("name") in {"Unknown", "N/A", "", None}) and code_data.get("contract_name"):
        meta["name"] = code_data.get("contract_name")
    return meta

@app.route('/api/v1/analyze', methods=['POST'])
def analyze_token():
    # Public API - no authentication required for analysis
    print("\n" + "="*50)
    print("[API] New Analysis Request Received")
    print("="*50)

    # 1. VALIDATE INCOMING DATA
    try:
        target_address, force_refresh = _parse_target_address()
        print(f"[API] Target Address: {target_address}")
    except ValidationError as e:
        print("[API] Validation Error: Bad Frontend Request")
        return jsonify({"success": False, "error_message": str(e)}), 400
    except ValueError as e:
        return jsonify({"success": False, "error_message": str(e)}), 400

    if scan_history_db.is_enabled() and not force_refresh:
        cached = scan_history_db.fetch_recent_full_response(
            target_address, "ethereum", "full", 10
        )
        if cached:
            body, scanned_at = cached
            print(f"[API] Returning cached full analysis (scanned_at={scanned_at})")
            return (
                jsonify(
                    _finalize_cached_analysis_response(target_address, body, scanned_at)
                ),
                200,
            )

    # Initialize our result containers
    detectors_output = {}
    simulation_output = {}

    try:
        # 2. FETCH SOURCE CODE
        # We fetch this just to make sure the contract exists and is verified
        code_data = etherscan_client.fetch_source_code(target_address)
        if code_data.get("status") == "Error":
             return jsonify({
                 "success": False, 
                 "contract_address": target_address,
                 "error_message": code_data["reason"]
             }), 400

        # 3. RUN STATIC DETECTORS
        print("\n[API] Booting Static Detectors...")
        detectors_output["taxes"] = _safe_run("taxes", tax_calc.check, target_address)
        detectors_output["liquidity"] = _safe_run("liquidity", liquidity_v1.check, target_address)
        detectors_output["holders"] = _safe_run("holders", holder_v1.check, target_address)
        detectors_output["transactions"] = _safe_run("transactions", transaction_v1.check, target_address)
        detectors_output["age"] = _safe_run("age", age_v1.check, target_address)
        detectors_output["minting"] = _safe_run("minting", minting_v1.check, target_address)
        detectors_output["rugpull"] = _safe_run("rugpull", rugpull_v1.check, target_address)
        
        # 4. RUN HYBRID AI/MATH DETECTOR
        # Since honeypot_v1 uses Slither, it will automatically pull the code itself
        detectors_output["honeypot"] = _safe_run("honeypot", honeypot_v1.check, target_address)
        _enrich_age_growth(detectors_output)

        # 5. RUN DYNAMIC SIMULATION SCENARIOS
        print("\n[API] Booting Dynamic Simulation Engine...")
        simulation_output = _safe_run("simulation", scenarios.run_stress_tests, target_address)

        # 6. CRUNCH THE FINAL SCORE
        print("\n[API] Calculating Final Risk Profile...")
        score_data = scoring_engine.calculate(detectors_output, simulation_output)
        category_risks = _compute_category_risks(detectors_output, simulation_output)
        
        risk_profile = RiskProfile(
            numeric_score=score_data["numeric_score"],
            risk_level=score_data["risk_level"],
            driving_factors=score_data["driving_factors"],
            confidence_score=_compute_confidence_score(detectors_output, simulation_output),
        )

        # 6.1 Generate a concise AI explanation from full context.
        ai_context = json.dumps({
            "contract_address": target_address,
            "risk_profile": risk_profile.model_dump(),
            "category_risks": category_risks,
            "detectors": detectors_output,
            "simulation": simulation_output,
        }, default=str)
        ai_summary = gemini_service.generate_report(ai_context)

        # 7. ASSEMBLE FINAL RESPONSE (Using Pydantic Schema)
        th_payload = _token_history_payload(target_address, risk_profile)
        final_response = AnalyzeResponse(
            success=True,
            contract_address=target_address,
            risk_profile=risk_profile,
            detectors=detectors_output,
            simulation={**simulation_output, "category_risks": category_risks, "analysis_mode": "full"},
            ai_summary=ai_summary,
            contract_source=_contract_source_for_response(code_data),
            token_metadata=_fetch_token_metadata(target_address, code_data),
            token_history=th_payload,
        )

        print(f"[API] Analysis Complete. Final Score: {risk_profile.numeric_score}/100")
        out = final_response.model_dump()
        scan_history_db.save_snapshot(
            target_address,
            "ethereum",
            out,
            scanned_by_username=session.get("user"),
        )

        # Return the cleanly formatted JSON
        return jsonify(out), 200

    except Exception as e:
        print(f"[API] CRITICAL SYSTEM ERROR: {str(e)}")
        return jsonify({
            "success": False,
            "contract_address": target_address,
            "error_message": "An internal server error occurred. Check server logs for details."
        }), 500


@app.route('/api/v1/analyze-lite', methods=['POST'])
def analyze_token_lite():
    """
    Fast analysis endpoint:
    - Runs lightweight detectors only
    - Skips Slither/Gemini/deep simulation for low latency
    - Keeps same response shape as /api/v1/analyze
    """
    # Public API - no authentication required for analysis
    print("\n" + "=" * 50)
    print("[API] New LITE Analysis Request Received")
    print("=" * 50)

    try:
        target_address, force_refresh = _parse_target_address()
        print(f"[API][LITE] Target Address: {target_address}")
    except ValidationError as e:
        return jsonify({"success": False, "error_message": str(e)}), 400
    except ValueError as e:
        return jsonify({"success": False, "error_message": str(e)}), 400

    if scan_history_db.is_enabled() and not force_refresh:
        cached = scan_history_db.fetch_recent_full_response(
            target_address, "ethereum", "lite", 10
        )
        if cached:
            body, scanned_at = cached
            print(f"[API][LITE] Returning cached lite analysis (scanned_at={scanned_at})")
            return (
                jsonify(
                    _finalize_cached_analysis_response(target_address, body, scanned_at)
                ),
                200,
            )

    detectors_output = {}
    simulation_output = {
        "status": "Skipped",
        "reason": "Lite mode skips dynamic simulation for faster response.",
        "max_buy_tax_detected": 0.0,
        "max_sell_tax_detected": 0.0,
        "detailed_breakdown": [],
    }

    try:
        # Keep contract existence/verification gate.
        code_data = etherscan_client.fetch_source_code(target_address)
        if code_data.get("status") == "Error":
            return jsonify({
                "success": False,
                "contract_address": target_address,
                "error_message": code_data["reason"]
            }), 400

        # Lightweight detector path.
        detectors_output["taxes"] = _safe_run("taxes", tax_calc.check, target_address)
        detectors_output["liquidity"] = _safe_run("liquidity", liquidity_v1.check, target_address)
        detectors_output["holders"] = _safe_run("holders", holder_v1.check, target_address)
        detectors_output["transactions"] = _safe_run("transactions", transaction_v1.check, target_address)
        detectors_output["age"] = _safe_run("age", age_v1.check, target_address)
        detectors_output["minting"] = _safe_run("minting", minting_v1.check, target_address)
        detectors_output["rugpull"] = _safe_run("rugpull", rugpull_v1.check, target_address)
        detectors_output["honeypot"] = {
            "status": "Skipped",
            "reason": "Lite mode skips heavy Slither/Gemini honeypot analysis."
        }
        _enrich_age_growth(detectors_output)

        score_data = scoring_engine.calculate(detectors_output, simulation_output)
        category_risks = _compute_category_risks(detectors_output, simulation_output)

        risk_profile = RiskProfile(
            numeric_score=score_data["numeric_score"],
            risk_level=score_data["risk_level"],
            driving_factors=score_data["driving_factors"],
            confidence_score=_compute_confidence_score(detectors_output, simulation_output),
        )

        th_payload = _token_history_payload(target_address, risk_profile)
        final_response = AnalyzeResponse(
            success=True,
            contract_address=target_address,
            risk_profile=risk_profile,
            detectors=detectors_output,
            simulation={**simulation_output, "category_risks": category_risks, "analysis_mode": "lite"},
            ai_summary="Lite analysis complete. Run /api/v1/analyze for deep honeypot simulation + AI summary.",
            contract_source=_contract_source_for_response(code_data),
            token_metadata=_fetch_token_metadata(target_address, code_data),
            token_history=th_payload,
        )
        out = final_response.model_dump()
        scan_history_db.save_snapshot(
            target_address,
            "ethereum",
            out,
            scanned_by_username=session.get("user"),
        )
        return jsonify(out), 200

    except Exception as e:
        print(f"[API][LITE] CRITICAL SYSTEM ERROR: {str(e)}")
        return jsonify({
            "success": False,
            "contract_address": target_address,
            "error_message": "An internal server error occurred. Check server logs for details."
        }), 500

# --- Server Boot ---
if __name__ == "__main__":
    print("BlockSentinel API Engine Starting...")
    debug_mode = os.getenv("FLASK_DEBUG", "false").strip().lower() == "true"
    # Run on port 5000, allow connections from outside
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
