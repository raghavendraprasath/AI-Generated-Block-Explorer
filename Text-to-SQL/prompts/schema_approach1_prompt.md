# Approach 1: LLM generates SQL schema directly from JSON

Used by `run_approach1.py` (loads `examples/getblock_100000.json` at runtime).

## System message

You are an expert SQLite database designer for Bitcoin blockchain data.
Output ONLY valid SQL DDL (CREATE TABLE statements), no explanation.

## User message

Below is a real Bitcoin Core RPC response from getblock(blockhash, 2).
Design a SQLite schema that stores ALL fields in this JSON.

Requirements:
- Use SQLite types (INTEGER, REAL, TEXT)
- Normalize arrays: tx[], vin[], vout[] should be separate tables where appropriate
- Include primary keys and foreign keys
- Output ONLY valid SQL DDL, no markdown fences or commentary

JSON:
{json}
