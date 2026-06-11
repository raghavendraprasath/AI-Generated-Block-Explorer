#!/usr/bin/env python3
"""Load Ethereum sample block and BTC daily price data into schema_extensions tables."""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from ingest import configure_sqlite, init_db

ROOT = Path(__file__).resolve().parent
DEFAULT_ETH = ROOT / "examples" / "eth_block_sample.json"
DEFAULT_PRICES = ROOT / "examples" / "btc_prices_sample.json"


def load_ethereum(conn: sqlite3.Connection, path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    conn.execute(
        """
        INSERT OR REPLACE INTO ethereum_blocks (
            number, hash, parent_hash, timestamp, gas_used, gas_limit,
            miner, transaction_count
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["number"],
            data["hash"],
            data.get("parentHash"),
            data["timestamp"],
            data.get("gasUsed"),
            data.get("gasLimit"),
            data.get("miner"),
            data.get("transactionCount"),
        ),
    )
    return 1


def load_prices(conn: sqlite3.Connection, path: Path) -> int:
    rows = json.loads(path.read_text(encoding="utf-8"))
    for row in rows:
        conn.execute(
            """
            INSERT OR REPLACE INTO btc_daily_prices (date, price_usd, source)
            VALUES (?, ?, ?)
            """,
            (row["date"], row["price_usd"], row["source"]),
        )
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest extension data (Ethereum, pricing)")
    parser.add_argument("--db", required=True, help="Absolute path to sqlite database")
    parser.add_argument("--schema", default=str(ROOT / "schema.sql"))
    parser.add_argument("--extensions", default=str(ROOT / "schema_extensions.sql"))
    parser.add_argument("--eth-json", default=str(DEFAULT_ETH))
    parser.add_argument("--prices-json", default=str(DEFAULT_PRICES))
    args = parser.parse_args()

    db_path = Path(args.db).resolve()
    if not db_path.is_absolute():
        print("ERROR: --db must be an absolute path", file=sys.stderr)
        return 1

    conn = sqlite3.connect(db_path)
    configure_sqlite(conn)
    init_db(conn, Path(args.schema), Path(args.extensions))

    eth_count = load_ethereum(conn, Path(args.eth_json))
    price_count = load_prices(conn, Path(args.prices_json))
    conn.commit()
    conn.close()

    print(f"Ingested {eth_count} Ethereum block(s) and {price_count} BTC price row(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
