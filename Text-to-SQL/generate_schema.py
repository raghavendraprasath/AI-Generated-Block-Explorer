#!/usr/bin/env python3
"""Auto-generate draft SQLite DDL from getblock(hash, 2) JSON (~99% automated)."""

import json
import sys
from pathlib import Path


def sql_type(value) -> str:
    if isinstance(value, bool):
        return "INTEGER"
    if isinstance(value, int):
        return "INTEGER"
    if isinstance(value, float):
        return "REAL"
    return "TEXT"


def flatten(obj, prefix=""):
    rows = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(value, (dict, list)):
                rows.extend(flatten(value, path))
            else:
                rows.append((path, sql_type(value)))
    elif isinstance(obj, list) and obj:
        rows.extend(flatten(obj[0], f"{prefix}[]"))
    return rows


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python3 generate_schema.py <input.json> <output.sql>")
        return 1

    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2])

    lines = [
        "-- AUTO-GENERATED DRAFT from getblock JSON",
        "-- Review and normalize into relational tables (see schema.sql)",
        "CREATE TABLE IF NOT EXISTS blocks_flat (",
        "    id INTEGER PRIMARY KEY AUTOINCREMENT,",
    ]

    seen = set()
    for path, typ in flatten(data):
        col = path.replace(".", "_").replace("[]", "_item").lower()
        if col in seen:
            continue
        seen.add(col)
        lines.append(f"    {col} {typ},")

    lines[-1] = lines[-1].rstrip(",")
    lines.append(");")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(seen)} columns to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())