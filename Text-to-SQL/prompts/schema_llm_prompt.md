# Schema Generation Bonus — Two Approaches

## Overview

Assignment §2a — auto-generated SQL schema from `getblock(hash, 2)` JSON.
We implemented **both** approaches, then manually produced `schema.sql`.

| | Approach 1 | Approach 2 |
|---|------------|------------|
| Method | LLM generates SQL directly from JSON | Python generates SQL from JSON |
| Input | `examples/getblock_100000.json` | same |
| Output | `prompts/schema_llm_direct.sql` | `schema_generated.sql` |
| Tool | `prompts/run_approach1.py` | `generate_schema.py` |
| Runtime LLM? | Yes (one-time) | No |

---

## Approach 1 — LLM → SQL directly (live run)

**Prompt:** `prompts/schema_approach1_prompt.md`  
**Run:** `python3 prompts/run_approach1.py` (requires `OPENROUTER_API_KEY`)  
**Output:** `prompts/schema_llm_direct.sql`

**Limitations observed (actual LLM output):**

- Invalid SQLite syntax: `vin TEXT[]`, `vout TEXT[]` (arrays not native in SQLite)
- Flat `bitcoin_tx` table duplicates vin/vout instead of normalizing
- Separate `bitcoin_vin` / `bitcoin_vout` with wrong PKs (`vin TEXT`, `vout TEXT`)
- Indexes reference non-existent columns (`bitcoin_vin.hash`, `bitcoin_vout.hash`)
- Missing block-level fields: `merkleroot`, `target`, `chainwork`, `coinbase_tx`, `mediantime`, `weight`
- Missing `scriptSig` asm/hex split, `scriptPubKey.address`, per-vout `scriptpubkey_type`
- No `sync_state`, no foreign keys to `block_height`
- Table names don't match final `blocks` / `transactions` / `transaction_inputs` / `transaction_outputs`

---

## Approach 2 — LLM writes code → SQL draft (§2a.ii.2)

**Prompt:** `prompts/schema_code_generation_prompt.md`  
**Implementation:** `generate_schema.py` → `schema_generated.sql` (39 columns, `blocks_flat`)

**Limitations observed:**

- Only flattens `tx[0]` (first transaction)
- Misses `fee`, `scriptSig`, and `address` from other transactions

**Prompt engineering notes:** `prompts/prompt_engineering_examples.md`

---

## Manual adjustments (both drafts → `schema.sql`)

1. Split into `blocks`, `coinbase_tx`, `transactions`, `transaction_inputs`, `transaction_outputs`
2. Added `sync_state`, foreign keys, and `txinwitness`
3. Added `fee`, `scriptSig`, `address` from all transactions
4. Renamed `versionHex` → `version_hex`, `nTx` → `ntx`
5. `ingest.py` implements the final schema (deterministic, 100% correct)
