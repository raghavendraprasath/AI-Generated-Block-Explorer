#!/usr/bin/env python3
"""Interactive chat UI for natural-language Bitcoin database questions."""

import argparse
import sys
from pathlib import Path

from text_to_sql import CANNOT_ANSWER, answer_question


def main() -> int:
    parser = argparse.ArgumentParser(description="Chat UI for Text-to-SQL")
    parser.add_argument("--db", required=True, help="Absolute path to sqlite database")
    parser.add_argument("--model", default="openrouter/free")
    args = parser.parse_args()

    db_path = Path(args.db).resolve()
    if not db_path.is_absolute():
        print("ERROR: --db must be an absolute path", file=sys.stderr)
        return 1
    if not db_path.exists():
        print(f"ERROR: database not found: {db_path}", file=sys.stderr)
        return 1

    print("Bitcoin Text-to-SQL Chat")
    print("Ask questions about blocks, transactions, Ethereum sample, or BTC prices.")
    print("Type 'quit' or 'exit' to leave.\n")

    while True:
        try:
            question = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return 0

        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            print("Bye.")
            return 0

        try:
            result = answer_question(question, db_path, model=args.model)
        except Exception as exc:
            print(f"Error: {exc}\n")
            continue

        if result.get("cannot_answer"):
            print(f"Assistant> {CANNOT_ANSWER}\n")
            continue

        print(f"SQL> {result['sql']}")
        print(f"Assistant> {result.get('answer', '')}\n")


if __name__ == "__main__":
    raise SystemExit(main())
