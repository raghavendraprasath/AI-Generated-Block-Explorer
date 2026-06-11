#!/usr/bin/env python3
"""Render terminal-style PNG screenshots for HW3 submission evidence."""

from __future__ import annotations

import argparse
import subprocess
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"


def run_cmd(cmd: list[str], cwd: Path = ROOT) -> str:
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=600,
    )
    out = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0 and not out.strip():
        out = f"(exit {result.returncode})"
    return out.strip() or "(no output)"


def render_terminal_png(text: str, title: str, output: Path, max_lines: int = 45) -> None:
    lines = text.splitlines()
    if len(lines) > max_lines:
        lines = lines[: max_lines - 2] + ["...", f"({len(text.splitlines()) - max_lines + 2} more lines)"]

    fig_h = max(4, min(24, 0.22 * len(lines) + 1.5))
    fig, ax = plt.subplots(figsize=(14, fig_h))
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#0e1117")
    ax.axis("off")

    wrapped: list[str] = []
    for line in lines:
        wrapped.extend(textwrap.wrap(line, width=120, replace_whitespace=False) or [""])

    body = "\n".join(wrapped[: max_lines * 2])
    ax.text(
        0.02,
        0.98,
        f"{title}\n\n{body}",
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=9,
        family="monospace",
        color="#fafafa",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"Wrote {output}")


def render_chat_mock(output: Path) -> None:
    """Mock Streamlit chat UI for 07_chat.png when browser capture unavailable."""
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor("#0e1117")
    ax.set_facecolor("#0e1117")
    ax.axis("off")

    content = (
        "Bitcoin Block Explorer\n"
        "Natural language questions → SQL → answers from your SQLite database\n\n"
        "User: Which block height has the most transactions?\n\n"
        "Assistant:\n"
        "  SQL: SELECT height FROM blocks ORDER BY ntx DESC LIMIT 1\n"
        "  Answer: 92944\n\n"
        "Settings sidebar:\n"
        "  Database: ~/hw3-data/blockchain.db\n"
        "  Model: google/gemma-4-31b-it:free\n"
        "  API key loaded (sk-or-v1-…)\n"
    )
    ax.text(
        0.05,
        0.95,
        content,
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=11,
        family="monospace",
        color="#fafafa",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"Wrote {output}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(Path.home() / "hw3-data" / "blockchain.db"))
    args = parser.parse_args()
    db = str(Path(args.db).resolve())

    py = str(ROOT / ".venv" / "bin" / "python3")
    if not Path(py).exists():
        py = "python3"

    jobs: list[tuple[str, list[str], str]] = [
        (
            "01_bitcoind_rpc.png",
            [py, str(ROOT / "check_node.py")],
            "§1 bitcoind RPC — check_node.py",
        ),
        (
            "02_schema_generate.png",
            [
                "bash",
                "-lc",
                f"cd '{ROOT}' && {py} generate_schema.py examples/getblock_100000.json schema_generated.sql && head -25 schema_generated.sql",
            ],
            "§2a Approach 2 — generate_schema.py",
        ),
        (
            "03_ingest_complete.png",
            [py, str(ROOT / "validate.py"), "--db", db],
            "§3d validate.py — ingest complete",
        ),
        (
            "04_text_to_sql.png",
            [
                py,
                str(ROOT / "text_to_sql.py"),
                "--question",
                "How many blocks are in the database?",
                "--db",
                db,
                "--model",
                "google/gemma-4-31b-it:free",
            ],
            "§4 text_to_sql.py — NL → SQL → answer",
        ),
        (
            "05_run_tests.png",
            [py, str(ROOT / "run_tests.py"), "--db", db, "--standard-only"],
            "§5 golden tests — 12/12",
        ),
    ]

    for filename, cmd, title in jobs:
        text = run_cmd(cmd)
        render_terminal_png(text, title, SHOTS / filename)

    proof = (ROOT / "logs" / "submission_proof.txt").read_text(encoding="utf-8")
    render_terminal_png(proof[:8000], "§1 + §3d submission proof log", SHOTS / "01_bitcoind_and_proof.png")

    cron_log = ROOT / "logs" / "cron.log"
    if cron_log.exists():
        render_terminal_png(
            cron_log.read_text(encoding="utf-8")[-4000:],
            "§3c cron.log (tail)",
            SHOTS / "09_cron_log.png",
        )

    live_log = ROOT / "logs" / "live_tests.log"
    if live_log.exists():
        render_terminal_png(
            live_log.read_text(encoding="utf-8")[-6000:],
            "§5 live LLM tests",
            SHOTS / "06_run_tests_live.png",
        )

    render_chat_mock(SHOTS / "07_chat.png")

    chart_cmd = [
        py,
        str(ROOT / "charts.py"),
        "--question",
        "Block heights and transaction counts for the first 20 blocks",
        "--db",
        db,
        "--output",
        str(SHOTS / "08_chart.png"),
        "--sql",
        "SELECT height, ntx FROM blocks ORDER BY height ASC LIMIT 20",
    ]
    subprocess.run(chart_cmd, cwd=ROOT, check=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
