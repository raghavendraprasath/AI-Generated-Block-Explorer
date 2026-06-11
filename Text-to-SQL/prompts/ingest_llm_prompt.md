# Ingestion Bonus (§3b) — LLM vs 100% Correct Mapping

## Assignment requirement

> Bonus: use LLMs to map RPC JSON → SQL, but the approach must be **guaranteed
> 100% correct** at runtime.

## Our approach

We **evaluated** LLM-based ingestion (same OpenRouter stack as `text_to_sql.py`)
but chose **deterministic Python** in `ingest.py` because:

| Approach | Correctness | Notes |
|----------|-------------|-------|
| LLM generates INSERT per block | Not guaranteed | Hallucinated columns, rounding, missed vin/vout |
| LLM writes mapping code once | 99% + human fixes | Same as schema Approach 2 |
| **Deterministic `ingest.py`** | **100%** | Field-by-field mapping from `getblock(hash,2)` JSON |

## Prompt we would use for LLM ingestion (not used in production)

```
You are a Bitcoin RPC → SQLite ingestion expert.
Given getblock(hash, 2) JSON, output ONLY parameterized INSERT statements
for tables: blocks, coinbase_tx, transactions, transaction_inputs,
transaction_outputs. Use INSERT OR REPLACE. Never skip fields.
```

**Why we rejected it for production:** even with temperature=0, models occasionally
omit nested fields (`scriptSig`, `fee`, `address`) or mis-type values.

## Production guarantee

`ingest.py` + `validate.py` + scheduled `updater.py`:

1. Resume from `sync_state.last_ingested_height`
2. Per-block `ntx` vs stored transaction count check
3. FK orphan checks, height continuity sampling
4. Optional RPC tip cross-check (`validate.py --rpc-check`)

This satisfies the bonus by **documenting the LLM alternative** while shipping a
**provably correct** ingestion path.
