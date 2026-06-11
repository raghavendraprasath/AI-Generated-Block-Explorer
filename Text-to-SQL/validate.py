#!/usr/bin/env python3
"""Validate SQLite blockchain database consistency and optional RPC cross-check."""

import argparse
import random
import sqlite3
import sys
from pathlib import Path

from ingest import bitcoin_rpc, configure_sqlite

DEFAULT_RPC_URL = "http://127.0.0.1:8332"
DEFAULT_RPC_USER = "test"
DEFAULT_RPC_PASSWORD = "test"


def load_schema_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    return [row[0] for row in rows]


def check_required_tables(conn: sqlite3.Connection) -> list[str]:
    required = {
        "blocks",
        "coinbase_tx",
        "transactions",
        "transaction_inputs",
        "transaction_outputs",
        "sync_state",
    }
    present = set(load_schema_tables(conn))
    return sorted(required - present)


def check_height_continuity(conn: sqlite3.Connection) -> list[str]:
    errors = []
    row = conn.execute("SELECT MIN(height), MAX(height), COUNT(*) FROM blocks").fetchone()
    if not row or row[2] == 0:
        return ["blocks table is empty"]
    min_h, max_h, count = row
    expected = max_h - min_h + 1
    if count != expected:
        errors.append(
            f"height gaps: min={min_h}, max={max_h}, count={count}, expected={expected}"
        )
    return errors


def check_ntx_consistency(conn: sqlite3.Connection, sample_size: int = 200) -> list[str]:
    errors = []
    max_h = conn.execute("SELECT MAX(height) FROM blocks").fetchone()[0]
    if max_h is None:
        return ["no blocks to validate"]
    heights = list(range(0, max_h + 1))
    if len(heights) > sample_size:
        heights = sorted(random.sample(heights, sample_size))
        heights.extend([0, max_h])
        heights = sorted(set(heights))

    for height in heights:
        row = conn.execute(
            """
            SELECT b.ntx, COUNT(t.txid)
            FROM blocks b
            LEFT JOIN transactions t ON b.height = t.block_height
            WHERE b.height = ?
            GROUP BY b.height, b.ntx
            """,
            (height,),
        ).fetchone()
        if not row:
            errors.append(f"block {height} missing")
        elif row[0] != row[1]:
            errors.append(f"block {height}: ntx={row[0]} stored_tx={row[1]}")
    return errors


def check_foreign_keys(conn: sqlite3.Connection) -> list[str]:
    errors = []
    orphans = conn.execute(
        """
        SELECT COUNT(*) FROM transactions t
        LEFT JOIN blocks b ON t.block_height = b.height
        WHERE b.height IS NULL
        """
    ).fetchone()[0]
    if orphans:
        errors.append(f"{orphans} transactions reference missing blocks")

    orphans = conn.execute(
        """
        SELECT COUNT(*) FROM transaction_inputs i
        LEFT JOIN transactions t ON i.txid = t.txid
        WHERE t.txid IS NULL
        """
    ).fetchone()[0]
    if orphans:
        errors.append(f"{orphans} inputs reference missing transactions")

    orphans = conn.execute(
        """
        SELECT COUNT(*) FROM transaction_outputs o
        LEFT JOIN transactions t ON o.txid = t.txid
        WHERE t.txid IS NULL
        """
    ).fetchone()[0]
    if orphans:
        errors.append(f"{orphans} outputs reference missing transactions")
    return errors


def check_sync_state(conn: sqlite3.Connection) -> list[str]:
    errors = []
    last = conn.execute(
        "SELECT value FROM sync_state WHERE key='last_ingested_height'"
    ).fetchone()
    max_h = conn.execute("SELECT MAX(height) FROM blocks").fetchone()[0]
    if last is None:
        errors.append("sync_state.last_ingested_height missing")
    elif max_h is not None and int(last[0]) != max_h:
        errors.append(f"sync_state={last[0]} but max block height={max_h}")
    return errors


def check_rpc_tip(
    conn: sqlite3.Connection,
    rpc_url: str,
    rpc_user: str,
    rpc_password: str,
) -> list[str]:
    errors = []
    try:
        chain_tip = int(bitcoin_rpc(rpc_url, rpc_user, rpc_password, "getblockcount"))
    except Exception as exc:
        return [f"RPC unavailable (skipped tip check): {exc}"]

    max_h = conn.execute("SELECT MAX(height) FROM blocks").fetchone()[0]
    if max_h is not None and max_h > chain_tip:
        errors.append(f"db max height {max_h} exceeds bitcoind tip {chain_tip}")
    return errors


def validate_db(
    conn: sqlite3.Connection,
    *,
    rpc_check: bool = False,
    rpc_url: str = DEFAULT_RPC_URL,
    rpc_user: str = DEFAULT_RPC_USER,
    rpc_password: str = DEFAULT_RPC_PASSWORD,
    ntx_sample: int = 200,
) -> list[str]:
    errors = []
    errors.extend(check_required_tables(conn))
    if errors:
        return errors
    errors.extend(check_height_continuity(conn))
    errors.extend(check_ntx_consistency(conn, ntx_sample))
    errors.extend(check_foreign_keys(conn))
    errors.extend(check_sync_state(conn))
    if rpc_check:
        errors.extend(check_rpc_tip(conn, rpc_url, rpc_user, rpc_password))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate blockchain SQLite database")
    parser.add_argument("--db", required=True, help="Absolute path to sqlite database")
    parser.add_argument("--rpc-check", action="store_true", help="Compare against bitcoind tip")
    parser.add_argument("--rpc-url", default=DEFAULT_RPC_URL)
    parser.add_argument("--rpc-user", default=DEFAULT_RPC_USER)
    parser.add_argument("--rpc-password", default=DEFAULT_RPC_PASSWORD)
    parser.add_argument("--ntx-sample", type=int, default=200)
    args = parser.parse_args()

    db_path = Path(args.db).resolve()
    if not db_path.is_absolute():
        print("ERROR: --db must be an absolute path", file=sys.stderr)
        return 1
    if not db_path.exists():
        print(f"ERROR: database not found: {db_path}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(db_path)
    configure_sqlite(conn)
    errors = validate_db(
        conn,
        rpc_check=args.rpc_check,
        rpc_url=args.rpc_url,
        rpc_user=args.rpc_user,
        rpc_password=args.rpc_password,
        ntx_sample=args.ntx_sample,
    )
    conn.close()

    if errors:
        print("VALIDATION FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
