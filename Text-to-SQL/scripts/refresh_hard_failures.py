#!/usr/bin/env python3
"""Refresh hard_failures.json expected/incorrect answers from live DB."""

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HARD_PATH = ROOT / "tests" / "hard_failures.json"


def main() -> int:
    db = sys.argv[1] if len(sys.argv) > 1 else str(Path.home() / "hw3-data" / "blockchain.db")
    cases = json.loads(HARD_PATH.read_text(encoding="utf-8"))
    conn = sqlite3.connect(db)

    for case in cases:
        case["expected_answer"] = conn.execute(case["expected_sql"]).fetchone()[0]
        case["incorrect_answer"] = conn.execute(case["incorrect_sql"]).fetchone()[0]

    conn.close()
    HARD_PATH.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {HARD_PATH} from {db}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
