# Prompt Engineering Examples (§2a.ii.1a)

Based on [promptingguide.ai](https://www.promptingguide.ai/) — small examples that
informed our schema-generation prompts.

---

## Example 1 — Be specific about output format

**Weak:**
```
Generate a database schema for this Bitcoin JSON.
```

**Strong:**
```
Design a SQLite schema for getblock(hash, 2) JSON.
Output ONLY CREATE TABLE statements. No markdown. No explanation.
Use INTEGER, REAL, TEXT. Normalize tx[], vin[], vout[] into separate tables.
```

**Lesson:** Constrain output format to reduce prose and hallucinated columns.

---

## Example 2 — Separate rules (system) from data (user)

**Weak:** One message mixing instructions and 9 KB of JSON.

**Strong:**
- **System:** role + output rules + SQLite type mapping
- **User:** the JSON instance only

**Lesson:** Matches assignment §4c.ii — task in system, instance in user.
Used in `schema_approach1_prompt.md` and `text_to_sql.py`.

---

## Example 3 — Ask for code instead of a one-shot artifact (§2a.ii.2)

**Weak:**
```
Give me a SQL schema for this JSON object.
```

**Strong:**
```
Write Python code that reads a getblock(hash, 2) JSON file and auto-generates
a normalized SQLite schema with separate tables for tx[], vin[], and vout[].
Map JSON types to SQLite types. Output a .sql file.
```

**Lesson:** Code generalizes to any block JSON; one-shot SQL often only fits `tx[0]`.
See `prompts/schema_code_generation_prompt.md` → `generate_schema.py`.

---

## Example 4 — Iterate on failure modes

| LLM output problem | Prompt fix |
|--------------------|------------|
| Markdown fences around SQL | Add "no markdown fences" |
| Flat single table | Add "normalize arrays into separate tables" |
| camelCase column names | Add "use snake_case" in manual review step |

**Lesson:** 99% automation + human review (`schema.sql`) is expected per assignment.
