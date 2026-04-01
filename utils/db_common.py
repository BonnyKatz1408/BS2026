"""
Shared MySQL connection settings for auth (users table) and scan history.
Supports both MYSQL_* (recommended) and legacy keys from the nested frontend .env
(HOST, DB, and AUTH_DB_USER / explicit MYSQL only — avoid relying on OS USER).
"""
from __future__ import annotations

import os
from pathlib import Path

_dotenv_loaded = False


def _load_project_dotenv() -> None:
    """Ensure .env beside this package is loaded (covers imports before main.py runs)."""
    global _dotenv_loaded
    if _dotenv_loaded:
        return
    _dotenv_loaded = True
    try:
        from dotenv import load_dotenv

        load_dotenv(Path(__file__).resolve().parent / ".env")
    except Exception:
        pass


def mysql_params() -> dict:
    _load_project_dotenv()
    host = os.getenv("MYSQL_HOST") or os.getenv("HOST") or "127.0.0.1"
    port = int(os.getenv("MYSQL_PORT") or "3306")
    user = (
        os.getenv("MYSQL_USER")
        or os.getenv("DB_USER")
        or os.getenv("AUTH_DB_USER")
        or "root"
    )
    password = (
        os.getenv("MYSQL_PASSWORD")
        or os.getenv("DB_PASSWORD")
        or os.getenv("PASSWORD")
        or os.getenv("AUTH_DB_PASSWORD")
        or ""
    )
    database = os.getenv("MYSQL_DATABASE") or os.getenv("DB") or "blocksentinel"
    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "charset": "utf8mb4",
    }
