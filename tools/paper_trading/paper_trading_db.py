"""
MySQL persistence for paper trading (virtual ETH balance + positions).
Controlled by PAPER_TRADING_ENABLED (or SCAN_HISTORY_ENABLED when unset) and MYSQL_*.
"""
from __future__ import annotations

import os
from decimal import Decimal
from typing import Any, Optional

import scan_history_db

_pymysql = None


def _load_pymysql():
    global _pymysql
    if _pymysql is None:
        import pymysql  # noqa: WPS433

        _pymysql = pymysql
    return _pymysql


def is_enabled() -> bool:
    v = os.getenv("PAPER_TRADING_ENABLED", "").strip().lower()
    if v in {"1", "true", "yes", "on"}:
        return True
    if v in {"0", "false", "no", "off"}:
        return False
    return scan_history_db.is_enabled()


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
    }


def _connect(autocommit: bool = True):
    pymysql = _load_pymysql()
    cfg = _config()
    from pymysql.cursors import DictCursor

    return pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        charset=cfg["charset"],
        cursorclass=DictCursor,
        autocommit=autocommit,
    )


DEFAULT_START_ETH = Decimal("10.000000000000000000")


def init_schema() -> None:
    if not is_enabled():
        return
    pymysql = _load_pymysql()
    sql_balance = """
    CREATE TABLE IF NOT EXISTS paper_user_balance (
      username VARCHAR(255) NOT NULL PRIMARY KEY,
      eth_balance DECIMAL(38, 18) NOT NULL DEFAULT 10.000000000000000000,
      updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    sql_positions = """
    CREATE TABLE IF NOT EXISTS paper_positions (
      id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
      username VARCHAR(255) NOT NULL,
      token_address VARCHAR(42) NOT NULL,
      chain VARCHAR(32) NOT NULL DEFAULT 'ethereum',
      token_symbol VARCHAR(64) NULL,
      token_name VARCHAR(255) NULL,
      tagline VARCHAR(512) NULL,
      pair_address VARCHAR(42) NULL,
      v3_fee INT NULL,
      quantity DECIMAL(38, 18) NOT NULL,
      cost_eth DECIMAL(38, 18) NOT NULL,
      avg_buy_price_eth DECIMAL(38, 18) NOT NULL,
      purchased_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
      status VARCHAR(16) NOT NULL DEFAULT 'open',
      closed_at DATETIME(3) NULL,
      sell_proceeds_eth DECIMAL(38, 18) NULL,
      exit_reason VARCHAR(32) NULL,
      INDEX idx_user_status (username, status),
      INDEX idx_user (username)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    try:
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(sql_balance)
                cur.execute(sql_positions)
                _ensure_v3_fee_column(cur)
                _ensure_exit_reason_column(cur)
                _ensure_paper_auto_settings_table(cur)
        finally:
            conn.close()
    except Exception as e:
        print(f"[paper_trading_db] init_schema skipped: {e}")


def _ensure_v3_fee_column(cur) -> None:
    try:
        cur.execute(
            """
            SELECT COUNT(*) AS c FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'paper_positions'
              AND COLUMN_NAME = 'v3_fee'
            """
        )
        row = cur.fetchone()
        cnt = int(row.get("c", 0)) if isinstance(row, dict) else int(row[0] if row else 0)
        if cnt > 0:
            return
    except Exception as e:
        print(f"[paper_trading_db] v3_fee column check: {e}")
        return
    try:
        cur.execute(
            "ALTER TABLE paper_positions ADD COLUMN v3_fee INT NULL AFTER pair_address"
        )
    except Exception as e2:
        print(f"[paper_trading_db] migrate v3_fee: {e2}")


def _ensure_exit_reason_column(cur) -> None:
    try:
        cur.execute(
            """
            SELECT COUNT(*) AS c FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'paper_positions'
              AND COLUMN_NAME = 'exit_reason'
            """
        )
        row = cur.fetchone()
        cnt = int(row.get("c", 0)) if isinstance(row, dict) else int(row[0] if row else 0)
        if cnt > 0:
            return
    except Exception as e:
        print(f"[paper_trading_db] exit_reason column check: {e}")
        return
    try:
        cur.execute(
            "ALTER TABLE paper_positions ADD COLUMN exit_reason VARCHAR(32) NULL AFTER sell_proceeds_eth"
        )
    except Exception as e2:
        print(f"[paper_trading_db] migrate exit_reason: {e2}")


def _ensure_paper_auto_settings_table(cur) -> None:
    sql = """
    CREATE TABLE IF NOT EXISTS paper_auto_settings (
      username VARCHAR(255) NOT NULL PRIMARY KEY,
      auto_exit_enabled TINYINT(1) NOT NULL DEFAULT 0,
      take_profit_pct DECIMAL(12, 6) NULL,
      stop_loss_pct DECIMAL(12, 6) NULL,
      ai_trading_enabled TINYINT(1) NOT NULL DEFAULT 0,
      dca_enabled TINYINT(1) NOT NULL DEFAULT 0,
      dca_token_address VARCHAR(42) NULL,
      dca_eth_amount DECIMAL(38, 18) NULL,
      dca_interval_minutes INT NULL,
      dca_last_run_at DATETIME(3) NULL,
      updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    try:
        cur.execute(sql)
        _ensure_ai_trading_column(cur)
    except Exception as e:
        print(f"[paper_trading_db] paper_auto_settings: {e}")


def _ensure_ai_trading_column(cur) -> None:
    try:
        cur.execute(
            """
            SELECT COUNT(*) AS c FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'paper_auto_settings'
              AND COLUMN_NAME = 'ai_trading_enabled'
            """
        )
        row = cur.fetchone()
        cnt = int(row.get("c", 0)) if isinstance(row, dict) else int(row[0] if row else 0)
        if cnt > 0:
            return
    except Exception as e:
        print(f"[paper_trading_db] ai_trading_enabled column check: {e}")
        return
    try:
        cur.execute(
            "ALTER TABLE paper_auto_settings ADD COLUMN ai_trading_enabled TINYINT(1) NOT NULL DEFAULT 0 AFTER stop_loss_pct"
        )
    except Exception as e2:
        print(f"[paper_trading_db] migrate ai_trading_enabled: {e2}")


def get_auto_settings(username: str) -> dict[str, Any]:
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT auto_exit_enabled, take_profit_pct, stop_loss_pct,
                       ai_trading_enabled,
                       dca_enabled, dca_token_address, dca_eth_amount,
                       dca_interval_minutes, dca_last_run_at
                FROM paper_auto_settings WHERE username=%s
                """,
                (username,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return {
            "auto_exit_enabled": False,
            "take_profit_pct": None,
            "stop_loss_pct": None,
            "ai_trading_enabled": False,
            "dca_enabled": False,
            "dca_token_address": None,
            "dca_eth_amount": None,
            "dca_interval_minutes": None,
            "dca_last_run_at": None,
        }

    def _f(v):
        if v is None:
            return None
        if isinstance(v, Decimal):
            return float(v)
        return v

    return {
        "auto_exit_enabled": bool(row.get("auto_exit_enabled")),
        "take_profit_pct": _f(row.get("take_profit_pct")),
        "stop_loss_pct": _f(row.get("stop_loss_pct")),
        "ai_trading_enabled": bool(row.get("ai_trading_enabled")),
        "dca_enabled": bool(row.get("dca_enabled")),
        "dca_token_address": row.get("dca_token_address"),
        "dca_eth_amount": _f(row.get("dca_eth_amount")),
        "dca_interval_minutes": int(row["dca_interval_minutes"])
        if row.get("dca_interval_minutes") is not None
        else None,
        "dca_last_run_at": row.get("dca_last_run_at"),
    }


def upsert_auto_settings(
    username: str,
    auto_exit_enabled: bool,
    take_profit_pct: Optional[float],
    stop_loss_pct: Optional[float],
    ai_trading_enabled: bool,
    dca_enabled: bool,
    dca_token_address: Optional[str],
    dca_eth_amount: Optional[Decimal],
    dca_interval_minutes: Optional[int],
) -> dict[str, Any]:
    conn = _connect(autocommit=False)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO paper_auto_settings (
                  username, auto_exit_enabled, take_profit_pct, stop_loss_pct,
                  ai_trading_enabled,
                  dca_enabled, dca_token_address, dca_eth_amount, dca_interval_minutes
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                  auto_exit_enabled=VALUES(auto_exit_enabled),
                  take_profit_pct=VALUES(take_profit_pct),
                  stop_loss_pct=VALUES(stop_loss_pct),
                  ai_trading_enabled=VALUES(ai_trading_enabled),
                  dca_enabled=VALUES(dca_enabled),
                  dca_token_address=VALUES(dca_token_address),
                  dca_eth_amount=VALUES(dca_eth_amount),
                  dca_interval_minutes=VALUES(dca_interval_minutes)
                """,
                (
                    username,
                    1 if auto_exit_enabled else 0,
                    take_profit_pct,
                    stop_loss_pct,
                    1 if ai_trading_enabled else 0,
                    1 if dca_enabled else 0,
                    dca_token_address,
                    str(dca_eth_amount) if dca_eth_amount is not None else None,
                    dca_interval_minutes,
                ),
            )
        conn.commit()
        return {"success": True}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error_message": str(e)}
    finally:
        conn.close()


def touch_dca_last_run(username: str) -> None:
    conn = _connect(autocommit=False)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE paper_auto_settings
                SET dca_last_run_at = CURRENT_TIMESTAMP(3)
                WHERE username=%s
                """,
                (username,),
            )
        conn.commit()
    except Exception:
        conn.rollback()
    finally:
        conn.close()


def ensure_user(username: str) -> Decimal:
    conn = _connect(autocommit=False)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT eth_balance FROM paper_user_balance WHERE username=%s FOR UPDATE",
                (username,),
            )
            row = cur.fetchone()
            if not row:
                cur.execute(
                    "INSERT INTO paper_user_balance (username, eth_balance) VALUES (%s, %s)",
                    (username, str(DEFAULT_START_ETH)),
                )
                conn.commit()
                return DEFAULT_START_ETH
            conn.commit()
            return Decimal(str(row["eth_balance"]))
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_balance(username: str) -> Decimal:
    ensure_user(username)
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT eth_balance FROM paper_user_balance WHERE username=%s",
                (username,),
            )
            row = cur.fetchone()
            return Decimal(str(row["eth_balance"])) if row else DEFAULT_START_ETH
    finally:
        conn.close()


def get_open_position(username: str, position_id: int) -> Optional[dict[str, Any]]:
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, token_address, chain, token_symbol, token_name, tagline,
                       pair_address, v3_fee, quantity, cost_eth, avg_buy_price_eth, purchased_at, status
                FROM paper_positions
                WHERE username=%s AND id=%s AND status='open'
                """,
                (username, position_id),
            )
            row = cur.fetchone()
            return row if row else None
    finally:
        conn.close()


def list_open_positions(username: str) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, token_address, chain, token_symbol, token_name, tagline,
                       pair_address, v3_fee, quantity, cost_eth, avg_buy_price_eth, purchased_at, status
                FROM paper_positions
                WHERE username=%s AND status='open'
                ORDER BY purchased_at DESC
                """,
                (username,),
            )
            return list(cur.fetchall() or [])
    finally:
        conn.close()


def list_closed_positions(username: str, limit: int = 50) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, token_address, chain, token_symbol, token_name, quantity, cost_eth,
                       sell_proceeds_eth, exit_reason, purchased_at, closed_at
                FROM paper_positions
                WHERE username=%s AND status='closed'
                ORDER BY closed_at DESC
                LIMIT %s
                """,
                (username, int(limit)),
            )
            return list(cur.fetchall() or [])
    finally:
        conn.close()


def add_balance(username: str, amount_eth: Decimal) -> dict[str, Any]:
    """Credit virtual ETH (paper top-up)."""
    if amount_eth <= 0:
        return {"success": False, "error_message": "Amount must be positive."}
    conn = _connect(autocommit=False)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT eth_balance FROM paper_user_balance WHERE username=%s FOR UPDATE",
                (username,),
            )
            row = cur.fetchone()
            if not row:
                cur.execute(
                    "INSERT INTO paper_user_balance (username, eth_balance) VALUES (%s, %s)",
                    (username, str(DEFAULT_START_ETH + amount_eth)),
                )
                new_bal = DEFAULT_START_ETH + amount_eth
            else:
                new_bal = Decimal(str(row["eth_balance"])) + amount_eth
                cur.execute(
                    "UPDATE paper_user_balance SET eth_balance=%s WHERE username=%s",
                    (str(new_bal), username),
                )
        conn.commit()
        return {"success": True, "balance_eth": float(new_bal)}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error_message": str(e)}
    finally:
        conn.close()


def buy_position(
    username: str,
    token_address: str,
    chain: str,
    token_symbol: str,
    token_name: str,
    tagline: Optional[str],
    pair_address: Optional[str],
    v3_fee: Optional[int],
    eth_spent: Decimal,
    quantity_tokens: Decimal,
    avg_buy_price_eth: Decimal,
    cost_eth: Decimal,
) -> dict[str, Any]:
    conn = _connect(autocommit=False)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT eth_balance FROM paper_user_balance WHERE username=%s FOR UPDATE",
                (username,),
            )
            row = cur.fetchone()
            if not row:
                cur.execute(
                    "INSERT INTO paper_user_balance (username, eth_balance) VALUES (%s, %s)",
                    (username, str(DEFAULT_START_ETH)),
                )
                bal = DEFAULT_START_ETH
            else:
                bal = Decimal(str(row["eth_balance"]))
            if bal < eth_spent:
                conn.rollback()
                return {"success": False, "error_message": "Insufficient virtual ETH balance."}
            new_bal = bal - eth_spent
            cur.execute(
                "UPDATE paper_user_balance SET eth_balance=%s WHERE username=%s",
                (str(new_bal), username),
            )
            cur.execute(
                """
                INSERT INTO paper_positions (
                  username, token_address, chain, token_symbol, token_name, tagline,
                  pair_address, v3_fee, quantity, cost_eth, avg_buy_price_eth, status
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'open')
                """,
                (
                    username,
                    token_address,
                    chain,
                    token_symbol,
                    token_name,
                    tagline if tagline else None,
                    pair_address,
                    v3_fee,
                    str(quantity_tokens),
                    str(cost_eth),
                    str(avg_buy_price_eth),
                ),
            )
            pid = cur.lastrowid
        conn.commit()
        return {"success": True, "position_id": pid, "balance_eth": float(new_bal)}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error_message": str(e)}
    finally:
        conn.close()


def sell_position(
    username: str,
    position_id: int,
    proceeds_eth: Decimal,
    exit_reason: Optional[str] = None,
) -> dict[str, Any]:
    conn = _connect(autocommit=False)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, quantity, status FROM paper_positions
                WHERE id=%s AND username=%s FOR UPDATE
                """,
                (position_id, username),
            )
            row = cur.fetchone()
            if not row or row["status"] != "open":
                conn.rollback()
                return {"success": False, "error_message": "Position not found or already closed."}
            cur.execute(
                "SELECT eth_balance FROM paper_user_balance WHERE username=%s FOR UPDATE",
                (username,),
            )
            brow = cur.fetchone()
            bal = Decimal(str(brow["eth_balance"])) if brow else Decimal(0)
            new_bal = bal + proceeds_eth
            cur.execute(
                "UPDATE paper_user_balance SET eth_balance=%s WHERE username=%s",
                (str(new_bal), username),
            )
            cur.execute(
                """
                UPDATE paper_positions
                SET status='closed', closed_at=NOW(3), sell_proceeds_eth=%s, exit_reason=%s
                WHERE id=%s
                """,
                (str(proceeds_eth), exit_reason, position_id),
            )
        conn.commit()
        return {"success": True, "balance_eth": float(new_bal), "sell_proceeds_eth": float(proceeds_eth)}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error_message": str(e)}
    finally:
        conn.close()


if is_enabled():
    init_schema()
