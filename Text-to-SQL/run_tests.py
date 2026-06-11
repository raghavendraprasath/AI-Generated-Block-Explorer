#!/usr/bin/env python3
"""Run Text-to-SQL test cases against the blockchain database."""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from text_to_sql import CANNOT_ANSWER, answer_question, format_rows

ROOT = Path(__file__).resolve().parent
DEFAULT_TESTS = ROOT / "tests" / "test_cases.json"
DEFAULT_HARD = ROOT / "tests" / "hard_failures.json"
DEFAULT_CANNOT = ROOT / "tests" / "cannot_answer_cases.json"
DEFAULT_EXTENSIONS = ROOT / "tests" / "extension_cases.json"


def normalize_answer(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    return str(value).strip()


def answers_match(expected: str, actual: str) -> bool:
    if expected == actual:
        return True
    try:
        e = float(expected)
        a = float(actual)
        return abs(e - a) < max(1e-6, abs(e) * 1e-6) or round(a, 8) == round(e, 8)
    except ValueError:
        return False


def execute_expected(conn: sqlite3.Connection, sql: str) -> str:
    rows = conn.execute(sql).fetchall()
    return format_rows(rows)


def run_standard_tests(conn: sqlite3.Connection, tests: list[dict], live: bool, db_path: Path) -> int:
    passed = 0
    failed = 0
    for index, case in enumerate(tests, start=1):
        question = case["question"]
        expected_sql = case["sql"]
        expected_answer = normalize_answer(case["answer"])
        actual_answer = normalize_answer(execute_expected(conn, expected_sql))

        ok = actual_answer == expected_answer
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] #{index}: {question}")
        if not ok:
            print(f"  expected answer: {expected_answer}")
            print(f"  actual answer:   {actual_answer}")
            failed += 1
            continue
        passed += 1

        if live:
            try:
                result = answer_question(question, db_path)
                llm_sql = result["sql"]
                llm_answer = normalize_answer(result.get("answer", ""))
                llm_ok = answers_match(expected_answer, llm_answer)
                tag = "LLM PASS" if llm_ok else "LLM FAIL"
                print(f"  [{tag}] generated SQL: {llm_sql}")
                if not llm_ok:
                    print(f"  LLM answer: {llm_answer}")
                    failed += 1
                    passed -= 1
            except Exception as exc:
                print(f"  [LLM ERROR] {exc}")
                failed += 1
                passed -= 1

    print(f"\nStandard tests: {passed} passed, {failed} failed")
    return failed


def run_hard_tests(conn: sqlite3.Connection, cases: list[dict], live: bool, db_path: Path) -> int:
    failed = 0
    for index, case in enumerate(cases, start=1):
        question = case["question"]
        expected_answer = normalize_answer(
            execute_expected(conn, case["expected_sql"])
        )
        stored_expected = normalize_answer(case["expected_answer"])
        ok = expected_answer == stored_expected
        print(f"[{'PASS' if ok else 'FAIL'}] hard #{index}: {question}")
        if not ok:
            print(f"  recomputed: {expected_answer}")
            print(f"  stored:     {stored_expected}")
            failed += 1

        if live:
            try:
                result = answer_question(question, db_path)
                llm_answer = normalize_answer(result.get("answer", ""))
                documented_wrong = normalize_answer(case.get("incorrect_answer", ""))
                if llm_answer == expected_answer:
                    print("  [LLM unexpectedly correct]")
                else:
                    print(f"  [LLM wrong as expected] {llm_answer}")
                    if documented_wrong and llm_answer != documented_wrong:
                        print(f"  documented incorrect answer: {documented_wrong}")
            except Exception as exc:
                print(f"  [LLM ERROR] {exc}")

    print(f"\nHard tests documented: {len(cases)} (expected to challenge the LLM)")
    return failed


def run_extension_tests(conn: sqlite3.Connection, tests: list[dict]) -> int:
    failed = 0
    for index, case in enumerate(tests, start=1):
        expected = normalize_answer(case["answer"])
        actual = normalize_answer(execute_expected(conn, case["sql"]))
        ok = expected == actual
        print(f"[{'PASS' if ok else 'FAIL'}] ext #{index}: {case['question']}")
        if not ok:
            print(f"  expected: {expected}, got: {actual}")
            failed += 1
    print(f"\nExtension tests: {len(tests) - failed} passed, {failed} failed")
    return failed


def run_cannot_answer_tests(cases: list[dict], live: bool, db_path: Path) -> int:
    if not live:
        print("\nSkipping CANNOT_ANSWER live tests (use --live).")
        return 0
    failed = 0
    for index, case in enumerate(cases, start=1):
        question = case["question"]
        try:
            result = answer_question(question, db_path)
            sql = result.get("sql", "")
            ok = result.get("cannot_answer") or sql.strip().upper() == CANNOT_ANSWER
            print(f"[{'PASS' if ok else 'FAIL'}] cannot #{index}: {question}")
            if not ok:
                print(f"  got SQL: {sql}")
                print(f"  got answer: {result.get('answer')}")
                failed += 1
        except Exception as exc:
            print(f"[FAIL] cannot #{index}: {exc}")
            failed += 1
    print(f"\nCANNOT_ANSWER tests: {len(cases) - failed} passed, {failed} failed")
    return failed


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Text-to-SQL test suite")
    parser.add_argument("--db", required=True, help="Absolute path to sqlite database")
    parser.add_argument("--tests", default=str(DEFAULT_TESTS))
    parser.add_argument("--hard", default=str(DEFAULT_HARD))
    parser.add_argument("--cannot", default=str(DEFAULT_CANNOT))
    parser.add_argument("--extensions", default=str(DEFAULT_EXTENSIONS))
    parser.add_argument("--live", action="store_true", help="Also query the LLM (needs API key)")
    parser.add_argument("--hard-only", action="store_true")
    parser.add_argument("--standard-only", action="store_true")
    args = parser.parse_args()

    db_path = Path(args.db).resolve()
    if not db_path.is_absolute():
        print("ERROR: --db must be an absolute path", file=sys.stderr)
        return 1

    conn = sqlite3.connect(db_path)
    failures = 0

    if not args.hard_only:
        tests = json.loads(Path(args.tests).read_text(encoding="utf-8"))
        failures += run_standard_tests(conn, tests, args.live, db_path)

    if not args.standard_only and Path(args.hard).exists():
        hard = json.loads(Path(args.hard).read_text(encoding="utf-8"))
        failures += run_hard_tests(conn, hard, args.live, db_path)

    if not args.hard_only and not args.standard_only and Path(args.extensions).exists():
        ext = json.loads(Path(args.extensions).read_text(encoding="utf-8"))
        failures += run_extension_tests(conn, ext)

    if not args.hard_only and not args.standard_only and Path(args.cannot).exists():
        cannot = json.loads(Path(args.cannot).read_text(encoding="utf-8"))
        failures += run_cannot_answer_tests(cannot, args.live, db_path)

    conn.close()
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
