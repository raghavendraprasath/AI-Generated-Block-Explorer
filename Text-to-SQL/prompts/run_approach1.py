#!/usr/bin/env python3
"""One-time: Approach 1 — ask LLM to generate SQL schema from getblock JSON."""
import os
import re
import sys
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from project_env import load_project_env

load_project_env()
JSON_PATH = ROOT / "examples" / "getblock_100000.json"
PROMPT_PATH = Path(__file__).resolve().parent / "schema_approach1_prompt.md"
OUT_PATH = ROOT / "prompts" / "schema_llm_direct.sql"


def load_user_prompt(json_path: Path, prompt_path: Path) -> tuple[str, str]:
    text = prompt_path.read_text(encoding="utf-8")
    system_match = re.search(
        r"## System message\s*\n+(.*?)(?=\n## |\Z)",
        text,
        re.DOTALL,
    )
    user_match = re.search(
        r"## User message\s*\n+(.*?)(?=\n## |\Z)",
        text,
        re.DOTALL,
    )
    if not system_match or not user_match:
        raise ValueError(f"Could not parse prompt sections in {prompt_path}")

    system = system_match.group(1).strip()
    user_template = user_match.group(1).strip()
    if "{json}" not in user_template:
        raise ValueError(f"User prompt in {prompt_path} must contain {{json}} placeholder")

    json_text = json_path.read_text(encoding="utf-8")
    user = user_template.replace("{json}", json_text)
    return system, user


def strip_sql_fences(sql: str) -> str:
    sql = sql.strip()
    fenced = re.match(r"^```(?:sql)?\s*\n(.*)\n```\s*$", sql, re.DOTALL | re.IGNORECASE)
    return fenced.group(1).strip() if fenced else sql


def main() -> int:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: set OPENROUTER_API_KEY before running Approach 1.", file=sys.stderr)
        return 1
    if not JSON_PATH.exists():
        print(f"ERROR: missing {JSON_PATH}", file=sys.stderr)
        return 1

    system, user = load_user_prompt(JSON_PATH, PROMPT_PATH)
    client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

    response = client.chat.completions.create(
        model="openrouter/free",
        temperature=0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )

    raw = response.choices[0].message.content or ""
    sql = strip_sql_fences(raw)
    OUT_PATH.write_text(sql + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
