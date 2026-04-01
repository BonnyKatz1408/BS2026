"""
Optional MySQL persistence for token analysis snapshots.
Controlled by SCAN_HISTORY_ENABLED and MYSQL_* environment variables.
Failing to connect never breaks analysis — operations are best-effort.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Optional

_pymysql = None


def _load_pymysql():
    global _pymysql
    if _pymysql is None:
        import pymysql  # noqa: WPS433

        _pymysql = pymysql
    return _pymysql


def is_enabled() -> bool:
    return os.getenv("SCAN_HISTORY_ENABLED", "").strip().lower() in {"1", "true", "yes", "on"}


def _config() -> dict:
    import db_common

    p = db_common.mysql_params()
    return {
        "host": p["host"],
        "port": int(p["port"]),
        "user": p["user"],
        "password": p["password"],
        "database": p["database"],
        "charset": p["charset"],
        "autocommit": True,
    }


def _connect():
    pymysql = _load_pymysql()
    cfg = _config()
    from pymysql.cursors import DictCursor

    cursorclass = DictCursor
    return pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        charset=cfg["charset"],
        cursorclass=cursorclass,
        autocommit=cfg["autocommit"],
    )


def init_schema() -> None:
    """Create table if missing. Idempotent."""
    if not is_enabled():
        return
    pymysql = _load_pymysql()
    sql = """
    CREATE TABLE IF NOT EXISTS token_scan_snapshots (
      id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      contract_address VARCHAR(42) NOT NULL,
      chain VARCHAR(32) NOT NULL DEFAULT 'ethereum',
      scanned_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
      analysis_mode VARCHAR(16) NOT NULL DEFAULT 'full',
      numeric_score INT NOT NULL,
      risk_level VARCHAR(32) NOT NULL,
      confidence_score INT NULL,
      honeypot_status VARCHAR(32) NULL,
      rugpull_status VARCHAR(32) NULL,
      liquidity_status VARCHAR(32) NULL,
      minting_status VARCHAR(32) NULL,
      sim_status VARCHAR(32) NULL,
      is_sellable TINYINT(1) NULL,
      token_symbol VARCHAR(64) NULL,
      token_name VARCHAR(255) NULL,
      scanned_by_username VARCHAR(255) NULL,
      snapshot_json JSON NOT NULL,
      full_response_json JSON NULL,
      INDEX idx_contract_scanned (contract_address, scanned_at),
      INDEX idx_scanned (scanned_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    try:
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                _ensure_username_column(cur)
                _ensure_full_response_column(cur)
        finally:
            conn.close()
    except Exception as e:
        print(f"[scan_history_db] init_schema skipped: {e}")


def _ensure_full_response_column(cur) -> None:
    """Store full /api/v1/analyze responses for short TTL cache (optional column on older installs)."""
    try:
        cur.execute(
            """
            SELECT COUNT(*) AS c FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='token_scan_snapshots'
              AND COLUMN_NAME='full_response_json'
            """
        )
        row = cur.fetchone()
        if isinstance(row, dict):
            cnt = int(row.get("c") or 0)
        else:
            cnt = int(row[0]) if row else 0
        if cnt > 0:
            return
    except Exception as e:
        print(f"[scan_history_db] full_response column check: {e}")
    try:
        cur.execute(
            "ALTER TABLE token_scan_snapshots ADD COLUMN full_response_json JSON NULL"
        )
    except Exception as e2:
        print(f"[scan_history_db] migrate full_response_json: {e2}")


def _ensure_username_column(cur) -> None:
    """Add scanned_by_username if table existed before that column."""
    try:
        cur.execute(
            """
            SELECT COUNT(*) AS c FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME='token_scan_snapshots'
              AND COLUMN_NAME='scanned_by_username'
            """
        )
        row = cur.fetchone()
        if isinstance(row, dict):
            cnt = int(row.get("c") or 0)
        else:
            cnt = int(row[0]) if row else 0
        if cnt > 0:
            return
    except Exception as e:
        print(f"[scan_history_db] column check: {e}")
    try:
        cur.execute(
            "ALTER TABLE token_scan_snapshots ADD COLUMN scanned_by_username VARCHAR(255) NULL"
        )
    except Exception as e2:
        print(f"[scan_history_db] migrate scanned_by_username: {e2}")


def _detectors_summary(detectors: dict) -> dict:
    out = {}
    for key in ("honeypot", "rugpull", "liquidity", "holders", "minting", "transactions", "taxes", "age"):
        block = detectors.get(key)
        if isinstance(block, dict):
            out[key] = {
                "status": block.get("status"),
                "reason": (str(block.get("reason", "") or ""))[:1200],
            }
        else:
            out[key] = {"status": None, "reason": None}
    return out


def _build_snapshot_json(payload: dict, scanned_by_username: Optional[str] = None) -> dict:
    """Compact JSON for history / audit trail."""
    rp = payload.get("risk_profile") or {}
    det = payload.get("detectors") or {}
    sim = payload.get("simulation") or {}
    meta = payload.get("token_metadata") or {}
    return {
        "numeric_score": rp.get("numeric_score"),
        "risk_level": rp.get("risk_level"),
        "confidence_score": rp.get("confidence_score"),
        "driving_factors": (rp.get("driving_factors") or [])[:12],
        "detectors_summary": _detectors_summary(det),
        "simulation": {
            "status": sim.get("status"),
            "is_sellable": sim.get("is_sellable"),
            "reason": (str(sim.get("reason") or sim.get("details") or ""))[:1200],
        },
        "token_metadata": {
            "name": meta.get("name"),
            "symbol": meta.get("symbol"),
        },
        "analysis_mode": sim.get("analysis_mode") or "unknown",
        "scanned_by_username": scanned_by_username,
    }


def _row_super_sus(row: dict) -> bool:
    try:
        score = int(row.get("numeric_score") or 0)
    except Exception:
        score = 0
    if score >= 78:
        return True
    if (row.get("honeypot_status") or "") == "High Risk":
        return True
    if (row.get("rugpull_status") or "") == "High Risk":
        return True
    if row.get("is_sellable") == 0:
        return True
    return False


def save_snapshot(
    contract_address: str,
    chain: str,
    analysis_response: dict,
    scanned_by_username: Optional[str] = None,
) -> bool:
    if not is_enabled():
        return False
    try:
        rp = analysis_response.get("risk_profile") or {}
        det = analysis_response.get("detectors") or {}
        sim = analysis_response.get("simulation") or {}
        meta = analysis_response.get("token_metadata") or {}
        hp = det.get("honeypot") or {}
        rpull = det.get("rugpull") or {}
        liq = det.get("liquidity") or {}
        mint = det.get("minting") or {}
        sellable = sim.get("is_sellable")
        is_sellable = None
        if sellable is True:
            is_sellable = 1
        elif sellable is False:
            is_sellable = 0
        snap = _build_snapshot_json(analysis_response, scanned_by_username=scanned_by_username)
        who = (scanned_by_username or None) and str(scanned_by_username)[:255]
        conn = _connect()
        try:
            with conn.cursor() as cur:
                full_json = json.dumps(analysis_response, ensure_ascii=False, default=str)
                cur.execute(
                    """
                    INSERT INTO token_scan_snapshots (
                      contract_address, chain, analysis_mode, numeric_score, risk_level,
                      confidence_score, honeypot_status, rugpull_status, liquidity_status,
                      minting_status, sim_status, is_sellable, token_symbol, token_name,
                      scanned_by_username, snapshot_json, full_response_json
                    ) VALUES (
                      %s,%s,%s,%s,%s,
                      %s,%s,%s,%s,
                      %s,%s,%s,%s,%s,
                      %s,%s,%s
                    )
                    """,
                    (
                        contract_address.lower(),
                        (chain or "ethereum").lower(),
                        str(snap.get("analysis_mode") or "full")[:16],
                        int(rp.get("numeric_score") or 0),
                        str(rp.get("risk_level") or "")[:32],
                        int(rp.get("confidence_score") or 0) if rp.get("confidence_score") is not None else None,
                        str(hp.get("status") or "")[:32] or None,
                        str(rpull.get("status") or "")[:32] or None,
                        str(liq.get("status") or "")[:32] or None,
                        str(mint.get("status") or "")[:32] or None,
                        str(sim.get("status") or "")[:32] or None,
                        is_sellable,
                        str(meta.get("symbol") or "")[:64] or None,
                        str(meta.get("name") or "")[:255] or None,
                        who,
                        json.dumps(snap, ensure_ascii=False),
                        full_json,
                    ),
                )
        finally:
            conn.close()
        return True
    except Exception as e:
        print(f"[scan_history_db] save_snapshot failed: {e}")
        return False


def fetch_history(contract_address: str, limit: int = 40) -> list[dict]:
    if not is_enabled():
        return []
    limit = max(1, min(int(limit), 100))
    try:
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, contract_address, chain, scanned_at, analysis_mode,
                           numeric_score, risk_level, confidence_score,
                           honeypot_status, rugpull_status, liquidity_status, minting_status,
                           sim_status, is_sellable, token_symbol, token_name,
                           scanned_by_username, snapshot_json
                    FROM token_scan_snapshots
                    WHERE contract_address = %s
                    ORDER BY scanned_at DESC, id DESC
                    LIMIT %s
                    """,
                    (contract_address.lower(), limit),
                )
                rows = cur.fetchall()
        finally:
            conn.close()
        for r in rows:
            if isinstance(r.get("scanned_at"), datetime):
                r["scanned_at"] = r["scanned_at"].isoformat()
            sj = r.get("snapshot_json")
            if isinstance(sj, str):
                try:
                    r["snapshot_json"] = json.loads(sj)
                except Exception:
                    r["snapshot_json"] = {}
            elif sj is None:
                r["snapshot_json"] = {}
        return rows
    except Exception as e:
        print(f"[scan_history_db] fetch_history failed: {e}")
        return []


def fetch_recent_full_response(
    contract_address: str,
    chain: str,
    analysis_mode: str,
    max_age_minutes: int = 10,
) -> Optional[tuple[dict, Any]]:
    """
    Return (full API response dict, scanned_at) when a recent row has full_response_json.
    Used to skip re-running detectors/simulation for the same token within a short window.
    """
    if not is_enabled():
        return None
    max_age_minutes = max(1, min(int(max_age_minutes), 24 * 60))
    try:
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT full_response_json, scanned_at
                    FROM token_scan_snapshots
                    WHERE contract_address = %s
                      AND chain = %s
                      AND analysis_mode = %s
                      AND full_response_json IS NOT NULL
                      AND scanned_at >= DATE_SUB(NOW(3), INTERVAL %s MINUTE)
                    ORDER BY scanned_at DESC, id DESC
                    LIMIT 1
                    """,
                    (
                        contract_address.lower(),
                        (chain or "ethereum").lower(),
                        str(analysis_mode)[:16],
                        max_age_minutes,
                    ),
                )
                row = cur.fetchone()
        finally:
            conn.close()
        if not row:
            return None
        raw = row.get("full_response_json")
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
            except Exception:
                return None
        elif isinstance(raw, dict):
            parsed = raw
        else:
            return None
        if not isinstance(parsed, dict) or not parsed.get("success"):
            return None
        return (parsed, row.get("scanned_at"))
    except Exception as e:
        print(f"[scan_history_db] fetch_recent_full_response failed: {e}")
        return None


def build_history_context_for_response(
    prior_rows: list[dict],
    current_numeric_score: int,
    current_risk_level: str,
) -> dict:
    """
    prior_rows: snapshots already in DB before the current scan is saved.
    """
    ctx: dict[str, Any] = {
        "database_enabled": True,
        "prior_scan_count": len(prior_rows),
        "surface_main_warning": False,
        "warning_title": None,
        "warning_detail": None,
        "how_we_decided": None,
        "historical_worst_score": None,
        "historical_worst_at": None,
    }
    if not prior_rows:
        ctx["how_we_decided"] = (
            "No prior rows in our database for this contract yet; this scan will be stored as the first snapshot."
        )
        return ctx

    worst = prior_rows[0]
    worst_score = int(worst.get("numeric_score") or 0)
    worst_at = worst.get("scanned_at")
    super_sus_any = any(_row_super_sus(r) for r in prior_rows)
    for r in prior_rows:
        sc = int(r.get("numeric_score") or 0)
        if sc >= worst_score:
            worst_score = sc
            worst = r
            worst_at = r.get("scanned_at")

    ctx["historical_worst_score"] = worst_score
    ctx["historical_worst_at"] = worst_at

    if not super_sus_any:
        ctx["how_we_decided"] = (
            "Past scans for this token did not reach our “high severity” historical threshold "
            "(score ≥78, honeypot/rug High Risk, or sell blocked), so we keep the main dashboard "
            "clean. Open Token History for the full timeline."
        )
        return ctx

    # Super-sus history: surface banner only if present scan looks materially safer (possible “rehab” narrative).
    cur = int(current_numeric_score or 0)
    improved = worst_score - cur >= 20
    now_moderate = cur <= 55

    if improved or now_moderate:
        ctx["surface_main_warning"] = True
        ctx["warning_title"] = "Historical scans flagged elevated risk — present reading looks calmer"
        ctx["warning_detail"] = (
            f"This contract appears in our database with past snapshots up to {worst_score}/100 risk. "
            f"Your current scan is {cur}/100 ({current_risk_level or 'n/a'}). "
            "That can reflect real improvement, relaunch/migration, changed liquidity, or different market "
            "conditions — not proof the earlier concern is gone. Review Token History for detector states over time."
        )
        ctx["how_we_decided"] = (
            "We flag this banner only when (1) at least one stored snapshot crosses severity thresholds "
            "(numeric score ≥78, honeypot or rugpull “High Risk”, or simulation marked not sellable), and "
            "(2) the new scan is at least 20 points lower than the worst stored score, or the new score is ≤55. "
            "Otherwise the main page stays clean so mild history does not clutter the view."
        )
    else:
        ctx["how_we_decided"] = (
            "Historical scans include high-severity signals, and the current scan remains elevated, "
            "so we do not add a separate “rehab” banner—risks are already visible in the main scores. "
            "Use Token History to compare past vs present detector summaries."
        )

    return ctx


# Initialise table on import when enabled (best-effort).
if is_enabled():
    init_schema()
