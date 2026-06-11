# Approach 2 — LLM writes code to generate schema (§2a.ii.2)

## Prompt used (paraphrased from assignment)

> Write code to auto-generate a SQL schema from a JSON object.

Full prompt:

```
Write Python code that reads a Bitcoin Core getblock(hash, 2) JSON file and
auto-generates a SQLite schema. Map JSON types to SQLite types (INTEGER, REAL,
TEXT). Flatten nested objects; for arrays use the first element as a template.
Output a .sql file with CREATE TABLE statements. Include a CLI:
  python3 generate_schema.py <input.json> <output.sql>
```

## Implementation

`generate_schema.py` — deterministic Python (reviewed and committed after LLM-assisted draft).

## Regenerate draft SQL

```bash
python3 generate_schema.py examples/getblock_100000.json schema_generated.sql
```

## Output

`schema_generated.sql` — 39-column `blocks_flat` draft.

## Manual fixes → `schema.sql`

Documented in `prompts/schema_llm_prompt.md`.
