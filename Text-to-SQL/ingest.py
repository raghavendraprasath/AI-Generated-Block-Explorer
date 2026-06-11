#!/usr/bin/env python3
"""Ingest Bitcoin blocks from bitcoind RPC into SQLite (deterministic, 100% correct)."""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

DEFAULT_RPC_URL = "http://127.0.0.1:8332"
DEFAULT_RPC_USER = "test"
DEFAULT_RPC_PASSWORD = "test"

_rpc_session: requests.Session | None = None


def get_rpc_session(rpc_url: str, rpc_user: str, rpc_password: str) -> requests.Session:
    global _rpc_session
    if _rpc_session is None:
        session = requests.Session()
        session.auth = HTTPBasicAuth(rpc_user, rpc_password)
        session.headers.update({"Content-Type": "application/json"})
        _rpc_session = session
    return _rpc_session


def bitcoin_rpc(rpc_url: str, rpc_user: str, rpc_password: str, method: str, params=None):
    if params is None:
        params = []
    session = get_rpc_session(rpc_url, rpc_user, rpc_password)
    response = session.post(
        rpc_url,
        json={"jsonrpc": "1.0", "id": "ingest", "method": method, "params": params},
        timeout=120,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("error"):
        raise RuntimeError(payload["error"])
    return payload["result"]


def configure_sqlite(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA temp_store=MEMORY")
    conn.execute("PRAGMA cache_size=-64000")
    conn.execute("PRAGMA foreign_keys=ON")


def init_db(conn: sqlite3.Connection, schema_path: Path, extensions_path: Path | None = None) -> None:
    conn.executescript(schema_path.read_text(encoding="utf-8"))
    if extensions_path and extensions_path.exists():
        conn.executescript(extensions_path.read_text(encoding="utf-8"))
    _migrate_schema(conn)


def _migrate_schema(conn: sqlite3.Connection) -> None:
    columns = {row[1] for row in conn.execute("PRAGMA table_info(transaction_inputs)")}
    if "txinwitness" not in columns:
        conn.execute("ALTER TABLE transaction_inputs ADD COLUMN txinwitness TEXT")


def get_sync_value(conn: sqlite3.Connection, key: str, default: str = "-1") -> str:
    row = conn.execute("SELECT value FROM sync_state WHERE key = ?", (key,)).fetchone()
    return row[0] if row else default


def set_sync_value(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO sync_state(key, value) VALUES(?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def insert_block(conn: sqlite3.Connection, block: dict) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO blocks (
            height, hash, confirmations, version, version_hex, merkleroot,
            time, mediantime, nonce, bits, target, difficulty, chainwork,
            ntx, previousblockhash, nextblockhash, strippedsize, size, weight
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            block.get("height"),
            block.get("hash"),
            block.get("confirmations"),
            block.get("version"),
            block.get("versionHex"),
            block.get("merkleroot"),
            block.get("time"),
            block.get("mediantime"),
            block.get("nonce"),
            block.get("bits"),
            block.get("target"),
            block.get("difficulty"),
            block.get("chainwork"),
            block.get("nTx"),
            block.get("previousblockhash"),
            block.get("nextblockhash"),
            block.get("strippedsize"),
            block.get("size"),
            block.get("weight"),
        ),
    )

    coinbase = block.get("coinbase_tx")
    if coinbase:
        conn.execute(
            """
            INSERT OR REPLACE INTO coinbase_tx (
                block_height, version, locktime, sequence, coinbase
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                block.get("height"),
                coinbase.get("version"),
                coinbase.get("locktime"),
                coinbase.get("sequence"),
                coinbase.get("coinbase"),
            ),
        )

    for tx in block.get("tx", []):
        txid = tx["txid"]
        conn.execute(
            """
            INSERT OR REPLACE INTO transactions (
                txid, block_height, hash, version, size, vsize, weight, locktime, fee, hex
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                txid,
                block.get("height"),
                tx.get("hash"),
                tx.get("version"),
                tx.get("size"),
                tx.get("vsize"),
                tx.get("weight"),
                tx.get("locktime"),
                tx.get("fee"),
                tx.get("hex"),
            ),
        )

        for vin_index, vin in enumerate(tx.get("vin", [])):
            is_coinbase = 1 if "coinbase" in vin else 0
            script_sig = vin.get("scriptSig", {})
            conn.execute(
                """
                INSERT OR REPLACE INTO transaction_inputs (
                    txid, vin_index, is_coinbase, spent_txid, spent_vout,
                    coinbase, scriptsig_asm, scriptsig_hex, sequence, txinwitness
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    txid,
                    vin_index,
                    is_coinbase,
                    vin.get("txid"),
                    vin.get("vout"),
                    vin.get("coinbase"),
                    script_sig.get("asm"),
                    script_sig.get("hex"),
                    vin.get("sequence"),
                    json.dumps(vin.get("txinwitness")) if vin.get("txinwitness") else None,
                ),
            )

        for vout in tx.get("vout", []):
            spk = vout.get("scriptPubKey", {})
            conn.execute(
                """
                INSERT OR REPLACE INTO transaction_outputs (
                    txid, vout_index, value, scriptpubkey_asm, scriptpubkey_desc,
                    scriptpubkey_hex, scriptpubkey_address, scriptpubkey_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    txid,
                    vout.get("n"),
                    vout.get("value"),
                    spk.get("asm"),
                    spk.get("desc"),
                    spk.get("hex"),
                    spk.get("address"),
                    spk.get("type"),
                ),
            )


def validate_block(conn: sqlite3.Connection, height: int) -> None:
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
        raise RuntimeError(f"Block {height} missing after ingest")
    if row[0] != row[1]:
        raise RuntimeError(
            f"Block {height}: ntx={row[0]} but stored transactions={row[1]}"
        )


def ingest_range(
    conn: sqlite3.Connection,
    rpc_url: str,
    rpc_user: str,
    rpc_password: str,
    start: int,
    end: int,
    commit_every: int = 1000,
    validate_every: int = 500,
) -> None:
    for height in range(start, end + 1):
        block_hash = bitcoin_rpc(rpc_url, rpc_user, rpc_password, "getblockhash", [height])
        block = bitcoin_rpc(rpc_url, rpc_user, rpc_password, "getblock", [block_hash, 2])
        insert_block(conn, block)

        if height % validate_every == 0 or height == end:
            validate_block(conn, height)

        if height % commit_every == 0:
            set_sync_value(conn, "last_ingested_height", str(height))
            conn.commit()
            print(f"Ingested through block {height}")

    set_sync_value(conn, "last_ingested_height", str(end))
    conn.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest bitcoind blocks into SQLite")
    parser.add_argument("--db", required=True, help="Absolute path to sqlite database")
    parser.add_argument("--schema", default="schema.sql", help="Path to schema.sql")
    parser.add_argument(
        "--extensions",
        default="schema_extensions.sql",
        help="Path to schema_extensions.sql (Ethereum, pricing)",
    )
    parser.add_argument("--rpc-url", default=DEFAULT_RPC_URL)
    parser.add_argument("--rpc-user", default=DEFAULT_RPC_USER)
    parser.add_argument("--rpc-password", default=DEFAULT_RPC_PASSWORD)
    parser.add_argument("--start", type=int, default=None)
    parser.add_argument("--end", type=int, default=None)
    parser.add_argument("--commit-every", type=int, default=1000)
    parser.add_argument("--validate-every", type=int, default=500)
    args = parser.parse_args()

    db_path = Path(args.db).resolve()
    schema_path = Path(args.schema).resolve()
    extensions_path = Path(args.extensions).resolve() if args.extensions else None

    if not db_path.is_absolute():
        print("ERROR: --db must be an absolute path", file=sys.stderr)
        return 1
    if not schema_path.exists():
        print(f"ERROR: schema not found at {schema_path}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(db_path)
    configure_sqlite(conn)
    init_db(conn, schema_path, extensions_path)

    try:
        chain_tip = int(bitcoin_rpc(args.rpc_url, args.rpc_user, args.rpc_password, "getblockcount"))
    except Exception as exc:
        print(f"ERROR: RPC failed — is bitcoind running? {exc}", file=sys.stderr)
        return 1

    if args.start is None:
        last = int(get_sync_value(conn, "last_ingested_height", "-1"))
        start = last + 1
    else:
        start = args.start

    end = chain_tip if args.end is None else min(args.end, chain_tip)

    if start > end:
        print(f"Nothing to ingest. last={start - 1}, chain_tip={chain_tip}")
        conn.close()
        return 0

    print(f"Ingesting blocks {start} to {end} (chain tip={chain_tip})")
    ingest_range(
        conn,
        args.rpc_url,
        args.rpc_user,
        args.rpc_password,
        start,
        end,
        commit_every=args.commit_every,
        validate_every=args.validate_every,
    )
    print("Ingest complete.")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())