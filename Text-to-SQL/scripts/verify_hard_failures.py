#!/usr/bin/env python3
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
cases = json.loads((ROOT / "tests" / "hard_failures.json").read_text())
db = sys.argv[1] if len(sys.argv) > 1 else str(Path.home() / "hw3-data" / "blockchain.db")
conn = sqlite3.connect(db)
for i, c in enumerate(cases, 1):
    exp = conn.execute(c["expected_sql"]).fetchone()[0]
    wrong = conn.execute(c["incorrect_sql"]).fetchone()[0]
    print(f"Case {i}: {c['question'][:50]}...")
    print(f"  expected SQL -> {exp!r} (stored {c['expected_answer']!r}) OK={str(exp)==str(c['expected_answer'])}")
    print(f"  incorrect SQL -> {wrong!r} (stored {c['incorrect_answer']!r}) OK={str(wrong)==str(c['incorrect_answer'])}")
    print(f"  answers differ: {exp != wrong}")
