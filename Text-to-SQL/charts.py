#!/usr/bin/env python3
"""Generate charts from natural-language questions via Text-to-SQL."""

import argparse
import sqlite3
import sys
from pathlib import Path

import matplotlib.pyplot as plt

from text_to_sql import CANNOT_ANSWER, answer_question


def build_figure(rows: list[tuple], title: str):
    """Build a matplotlib figure from query rows (for CLI or Streamlit)."""
    if not rows:
        raise ValueError("No data to chart")

    fig, ax = plt.subplots(figsize=(10, 5))

    if len(rows[0]) == 1:
        values = [row[0] for row in rows]
        labels = [str(i) for i in range(len(values))]
        ax.bar(labels, values)
        ax.tick_params(axis="x", rotation=45)
    elif len(rows[0]) == 2:
        x_vals = [row[0] for row in rows]
        y_vals = [row[1] for row in rows]
        if all(isinstance(x, (int, float)) for x in x_vals):
            ax.plot(x_vals, y_vals, marker="o")
            ax.set_xlabel("Column 1")
            ax.set_ylabel("Column 2")
        else:
            ax.bar([str(x) for x in x_vals], y_vals)
            ax.tick_params(axis="x", rotation=45)
    else:
        plt.close(fig)
        raise ValueError("Chart supports 1- or 2-column result sets only")

    ax.set_title(title)
    fig.tight_layout()
    return fig


def plot_rows(rows: list[tuple], title: str, output: Path) -> None:
    fig = build_figure(rows, title)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=150)
    plt.close(fig)
    print(f"Wrote chart to {output}")


def fetch_chart_data(
    question: str,
    db_path: Path,
    *,
    sql: str | None = None,
    api_key: str | None = None,
    model: str = "openrouter/free",
) -> tuple[str, list[tuple]]:
    """Return (sql, rows) for charting."""
    if sql:
        conn = sqlite3.connect(db_path)
        rows = conn.execute(sql).fetchall()
        conn.close()
        return sql, rows

    result = answer_question(question, db_path, api_key=api_key, model=model)
    if result.get("cannot_answer"):
        raise ValueError(CANNOT_ANSWER)
    return result["sql"], result.get("rows", [])


CHART_PRESETS = [
    {
        "label": "Early blocks · height vs tx count",
        "question": "Block heights and transaction counts for the first 20 blocks",
        "sql": "SELECT height, ntx FROM blocks ORDER BY height ASC LIMIT 20",
    },
    {
        "label": "Busiest blocks · top 15 by transactions",
        "question": "Which blocks have the most transactions?",
        "sql": "SELECT height, ntx FROM blocks ORDER BY ntx DESC LIMIT 15",
    },
    {
        "label": "BTC price history · sample dates",
        "question": "BTC USD prices from our pricing table",
        "sql": "SELECT date, price_usd FROM btc_daily_prices ORDER BY date",
    },
]


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
            sql, rows = fetch_chart_data(
                args.question, db_path, model=args.model
            )
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    print(f"SQL: {sql}")
    try:
        plot_rows(rows, args.question[:80], output)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
