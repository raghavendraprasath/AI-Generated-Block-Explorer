#!/usr/bin/env python3
"""Natural language questions → SQL → answers from the Bitcoin SQLite database."""

import argparse
import os
import re
import sqlite3
import sys
from pathlib import Path

from openai import OpenAI

from project_env import get_openrouter_api_key, load_project_env

load_project_env()

# Assignment §4c.i exact system prompt:
CORE_SYSTEM_PROMPT = (
    "You are a SQL developer that is expert in Bitcoin and you answer natural "
    "language questions about the bitcoind database in a sqlite database. You "
    "always only respond with SQL statements that are correct."
)

# Assignment §4c.i — system role is ONLY the task description (exact text above).
SYSTEM_PROMPT = CORE_SYSTEM_PROMPT

# Notes optional extension — CANNOT_ANSWER instruction goes in the user message (instance).
CANNOT_ANSWER_USER_NOTE = (
    "If the question cannot be answered using only the schema above, respond with "
    "exactly: CANNOT_ANSWER. This includes: live/real-time prices, stock market data, "
    "weather, blockchains not in the schema (Dogecoin, Solana, etc.), and any topic "
    "with no matching tables. Do NOT query btc_daily_prices for live prices or "
    "unrelated questions. Otherwise return one SQLite SELECT with spaces after keywords "
    "(e.g. SELECT COUNT(*))."
)

CANNOT_ANSWER = "CANNOT_ANSWER"
DEFAULT_MODEL = "google/gemma-4-31b-it:free"


def load_schema_ddl(conn: sqlite3.Connection) -> str:
    rows = conn.execute(
        """
        SELECT sql FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%' AND sql IS NOT NULL
        ORDER BY name
        """
    ).fetchall()
    return "\n\n".join(row[0] for row in rows)


def strip_sql_fences(text: str) -> str:
    text = text.strip()
    fenced = re.match(r"^```(?:sql)?\s*\n(.*)\n```\s*$", text, re.DOTALL | re.IGNORECASE)
    return fenced.group(1).strip() if fenced else text


def clean_generated_sql(text: str) -> str:
    """Normalize common free-model artifacts before execution."""
    sql = strip_sql_fences(text).strip().rstrip(";")
    if sql.upper() == CANNOT_ANSWER:
        return CANNOT_ANSWER

    # Drop leading non-SQL preamble (e.g. "User Safety: safe")
    select_match = re.search(r"\b(WITH|SELECT)\b", sql, re.IGNORECASE)
    if select_match:
        sql = sql[select_match.start() :]

    # Fix SELECTCOUNT / SELECTntx style missing whitespace after SELECT
    sql = re.sub(r"(?i)^SELECT(?=[A-Za-z_*])", "SELECT ", sql)
    sql = re.sub(r"\s+", " ", sql).strip()
    return sql


def is_safe_select(sql: str) -> bool:
    normalized = re.sub(r"\s+", " ", sql.strip().lower())
    if normalized == "cannot_answer":
        return False
    if ";" in normalized.rstrip(";"):
        return False
    forbidden = (
        "insert ",
        "update ",
        "delete ",
        "drop ",
        "alter ",
        "create ",
        "attach ",
        "detach ",
        "pragma ",
        "replace ",
    )
    if any(token in normalized for token in forbidden):
        return False
    return normalized.startswith("select") or normalized.startswith("with")


def generate_sql(
    question: str,
    schema_ddl: str,
    *,
    api_key: str | None = None,
    model: str = DEFAULT_MODEL,
) -> str:
    key = api_key or get_openrouter_api_key()
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=key, base_url="https://openrouter.ai/api/v1")
    user_content = (
        "SQLite schema:\n"
        f"{schema_ddl}\n\n"
        "Natural language question:\n"
        f"{question}\n\n"
        f"{CANNOT_ANSWER_USER_NOTE}"
    )
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )
    return clean_generated_sql(response.choices[0].message.content or "")


def execute_sql(conn: sqlite3.Connection, sql: str) -> list[tuple]:
    cursor = conn.execute(sql)
    return cursor.fetchall()


def format_rows(rows: list[tuple]) -> str:
    if not rows:
        return "(no rows)"
    if len(rows) == 1 and len(rows[0]) == 1:
        return str(rows[0][0])
    return "\n".join(str(row) for row in rows)


def answer_question(
    question: str,
    db_path: Path,
    *,
    api_key: str | None = None,
    model: str = DEFAULT_MODEL,
    execute: bool = True,
) -> dict:
    conn = sqlite3.connect(db_path)
    try:
        schema_ddl = load_schema_ddl(conn)
        sql = generate_sql(question, schema_ddl, api_key=api_key, model=model)

        if sql.strip().upper() == CANNOT_ANSWER:
            return {
                "question": question,
                "sql": CANNOT_ANSWER,
                "answer": CANNOT_ANSWER,
                "cannot_answer": True,
            }

        if not is_safe_select(sql):
            raise ValueError(f"Refusing to run unsafe SQL: {sql}")

        result = {
            "question": question,
            "sql": sql,
            "cannot_answer": False,
        }
        if execute:
            rows = execute_sql(conn, sql)
            result["answer"] = format_rows(rows)
            result["rows"] = rows
        return result
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Text-to-SQL for Bitcoin blockchain DB")
    parser.add_argument("--question", required=True, help="Natural language question")
    parser.add_argument("--db", required=True, help="Absolute path to sqlite database")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--sql-only", action="store_true", help="Print SQL only, do not execute")
    args = parser.parse_args()

    db_path = Path(args.db).resolve()
    if not db_path.is_absolute():
        print("ERROR: --db must be an absolute path", file=sys.stderr)
        return 1
    if not db_path.exists():
        print(f"ERROR: database not found: {db_path}", file=sys.stderr)
        return 1

    try:
        result = answer_question(
            args.question,
            db_path,
            model=args.model,
            execute=not args.sql_only,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("SQL:")
    print(result["sql"])
    if not args.sql_only:
        print("\nAnswer:")
        print(result.get("answer", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
