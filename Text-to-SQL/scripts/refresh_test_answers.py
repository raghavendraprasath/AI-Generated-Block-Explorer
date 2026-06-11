#!/usr/bin/env python3
"""Refresh test_cases.json answers from the live database."""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
cases_path = ROOT / "tests" / "test_cases.json"
db = Path(sys.argv[1] if len(sys.argv) > 1 else Path.home() / "hw3-data" / "blockchain.db")

cases = json.loads(cases_path.read_text(encoding="utf-8"))
conn = sqlite3.connect(str(db))
for case in cases:
    case["answer"] = conn.execute(case["sql"]).fetchone()[0]
conn.close()

cases_path.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
print(f"Updated {cases_path} from {db}")
