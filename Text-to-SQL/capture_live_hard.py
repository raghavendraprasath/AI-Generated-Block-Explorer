#!/usr/bin/env python3
"""Capture live LLM SQL/answers for hard-failure cases (requires OPENROUTER_API_KEY)."""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from text_to_sql import answer_question, format_rows

ROOT = Path(__file__).resolve().parent
DEFAULT_HARD = ROOT / "tests" / "hard_failures.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture live LLM outputs for hard tests")
    parser.add_argument("--db", required=True)
    parser.add_argument("--hard", default=str(DEFAULT_HARD))
    parser.add_argument("--write", action="store_true", help="Update hard_failures.json in place")
    args = parser.parse_args()

    db_path = Path(args.db).resolve()
    hard_path = Path(args.hard)
    cases = json.loads(hard_path.read_text(encoding="utf-8"))
    conn = sqlite3.connect(db_path)

    for case in cases:
        question = case["question"]
        print(f"\n=== {question}")
        expected = str(case.get("expected_answer", "")).strip()
        try:
            result = answer_question(question, db_path)
            live_sql = result["sql"]
            case["live_sql"] = live_sql
            if result.get("cannot_answer"):
                live_answer = "CANNOT_ANSWER"
            else:
                try:
                    rows = conn.execute(live_sql).fetchall()
                    live_answer = format_rows(rows)
                except Exception as exc:
                    live_answer = f"SQL error: {exc}"
            case["live_answer"] = live_answer
            print("live SQL:", live_sql)
            print("live answer:", live_answer)

            if live_answer != expected and not live_answer.startswith("SQL error"):
                case["incorrect_sql"] = live_sql
                case["incorrect_answer"] = live_answer
                print("  -> recorded as incorrect (differs from expected)")
            elif live_answer.startswith("SQL error"):
                case["incorrect_sql"] = live_sql
                case["incorrect_answer"] = live_answer
                print("  -> recorded as incorrect (SQL error)")
            else:
                print("  -> LLM correct; kept documented incorrect_sql")
        except Exception as exc:
            print("ERROR:", exc)

    conn.close()
    if args.write:
        hard_path.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
        print(f"\nUpdated {hard_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
