#!/usr/bin/env python3
"""Generate charts from natural-language questions via Text-to-SQL."""

import argparse
import sqlite3
import sys
from pathlib import Path

import matplotlib.pyplot as plt

from text_to_sql import CANNOT_ANSWER, answer_question


def plot_rows(rows: list[tuple], title: str, output: Path) -> None:
    if not rows:
        raise ValueError("No data to chart")

    if len(rows[0]) == 1:
        values = [row[0] for row in rows]
        labels = [str(i) for i in range(len(values))]
        plt.bar(labels, values)
        plt.xticks(rotation=45, ha="right")
    elif len(rows[0]) == 2:
        x_vals = [row[0] for row in rows]
        y_vals = [row[1] for row in rows]
        if all(isinstance(x, (int, float)) for x in x_vals):
            plt.plot(x_vals, y_vals, marker="o")
            plt.xlabel(str(0))
            plt.ylabel(str(1))
        else:
            plt.bar([str(x) for x in x_vals], y_vals)
            plt.xticks(rotation=45, ha="right")
    else:
        raise ValueError("Chart supports 1- or 2-column result sets only")

    plt.title(title)
    plt.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=150)
    plt.close()
    print(f"Wrote chart to {output}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Chart generation from Text-to-SQL")
    parser.add_argument("--question", required=True, help="Natural language question")
    parser.add_argument("--db", required=True, help="Absolute path to sqlite database")
    parser.add_argument("--output", default="charts/output.png", help="Output image path")
    parser.add_argument("--model", default="openrouter/free")
    parser.add_argument(
        "--sql",
        help="Skip LLM; run this SQL directly (for deterministic chart generation)",
    )
    args = parser.parse_args()

    db_path = Path(args.db).resolve()
    output = Path(args.output).resolve()
    if not db_path.is_absolute():
        print("ERROR: --db must be an absolute path", file=sys.stderr)
        return 1

    if args.sql:
        conn = sqlite3.connect(db_path)
        rows = conn.execute(args.sql).fetchall()
        conn.close()
        sql = args.sql
    else:
        try:
            result = answer_question(args.question, db_path, model=args.model)
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

        if result.get("cannot_answer"):
            print(CANNOT_ANSWER)
            return 1

        rows = result.get("rows", [])
        sql = result["sql"]

    print(f"SQL: {sql}")
    try:
        plot_rows(rows, args.question[:80], output)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
