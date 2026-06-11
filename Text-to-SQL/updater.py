#!/usr/bin/env python3
"""Keep the SQLite database synced with bitcoind (for cron / manual runs)."""

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "logs"


def log(message: str, log_file: Path | None) -> None:
    line = f"{datetime.now(timezone.utc).isoformat()} {message}"
    print(line)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def run_step(cmd: list[str], log_file: Path | None) -> int:
    log(f"RUN {' '.join(cmd)}", log_file)
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        log(f"FAILED exit={result.returncode}", log_file)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Update blockchain SQLite DB from bitcoind")
    parser.add_argument("--db", required=True, help="Absolute path to sqlite database")
    parser.add_argument("--schema", default=str(ROOT / "schema.sql"))
    parser.add_argument("--rpc-url", default="http://127.0.0.1:8332")
    parser.add_argument("--rpc-user", default="test")
    parser.add_argument("--rpc-password", default="test")
    parser.add_argument("--skip-validate", action="store_true")
    parser.add_argument("--log-file", default=None, help="Append log output to this file")
    args = parser.parse_args()

    db_path = Path(args.db).resolve()
    if not db_path.is_absolute():
        print("ERROR: --db must be an absolute path", file=sys.stderr)
        return 1

    log_file = Path(args.log_file).resolve() if args.log_file else LOG_DIR / "updater.log"
    py = sys.executable

    ingest_cmd = [
        py,
        str(ROOT / "ingest.py"),
        "--db",
        str(db_path),
        "--schema",
        args.schema,
        "--rpc-url",
        args.rpc_url,
        "--rpc-user",
        args.rpc_user,
        "--rpc-password",
        args.rpc_password,
    ]
    if run_step(ingest_cmd, log_file) != 0:
        return 1

    extensions_cmd = [
        py,
        str(ROOT / "ingest_extensions.py"),
        "--db",
        str(db_path),
    ]
    if run_step(extensions_cmd, log_file) != 0:
        return 1

    if not args.skip_validate:
        validate_cmd = [
            py,
            str(ROOT / "validate.py"),
            "--db",
            str(db_path),
            "--rpc-check",
            "--rpc-url",
            args.rpc_url,
            "--rpc-user",
            args.rpc_user,
            "--rpc-password",
            args.rpc_password,
        ]
        if run_step(validate_cmd, log_file) != 0:
            return 1

    log("Update complete.", log_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
