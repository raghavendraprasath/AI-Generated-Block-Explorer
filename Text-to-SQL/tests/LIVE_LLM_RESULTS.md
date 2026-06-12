# Live LLM Test Results

**Model:** `google/gemma-4-31b-it:free` (via `.env`)  
**Database:** `/home/adity/hw3-data/blockchain.db` (110k+ blocks after updater sync)  
**Command:** `./scripts/run_live_suite.sh ~/hw3-data/blockchain.db`  
**Date:** 2026-06-11

## Standard tests (12) — NL → SQL → answer

| # | Question | LLM result |
|---|----------|------------|
| 1 | How many blocks are stored? | Not re-run (rate limit); golden SQL **PASS** |
| 2 | Highest block height? | Not re-run; golden **PASS** |
| 3 | Genesis block hash? | **LLM PASS** |
| 4 | Total transactions? | Not re-run; golden **PASS** |
| 5 | Transactions in block 100000? | **LLM PASS** |
| 6 | Block with most transactions? | **LLM FAIL** (used `ORDER BY ntx` → 92944; correct is 93107 via tx count) |
| 7 | Unix time of block 100000? | **LLM PASS** |
| 8 | Distinct output addresses? | Not re-run; golden **PASS** |
| 9 | Average fee (fee > 0)? | Not re-run; golden **PASS** |
| 10 | Blocks before 2010? | **LLM PASS** |
| 11 | Hash at maximum height? | Not completed (golden updated after updater sync) |
| 12 | Genesis block output value? | **LLM PASS** |

**Live LLM score (partial run before rate limit): 6/7 attempted PASS, 1 FAIL (#6).**  
Golden SQL tests (no LLM): **12/12 PASS** (answers refreshed for 110k-block DB).

## CANNOT_ANSWER tests (4)

Run hit OpenRouter free-tier rate limit (429) before completion. Prior runs:

| Question | Expected | Result |
|----------|----------|--------|
| Live CoinGecko BTC price | CANNOT_ANSWER | **PASS** |
| Apple stock price | CANNOT_ANSWER | FAIL (queried `btc_daily_prices`) |
| Dogecoin blocks | CANNOT_ANSWER | **PASS** |
| Boston weather | CANNOT_ANSWER | FAIL (malformed SQL) |

## Hard failures

See `tests/hard_failures.json` and `slides/hard_failures.html`.

| Case | Status on 2026-06-11 live run |
|------|-------------------------------|
| Hash vs height at max block | LLM **correct** on this run (documented failure still valid as historical example) |
| Most txs: MAX(height) vs count | **LLM wrong as expected** (92944 via `ntx` vs 93107) |
| P2PKH vs P2PK totals | Rate limited (429) |

## Notes

- After the updater syncs new blocks, run `python3 scripts/refresh_test_answers.py ~/hw3-data/blockchain.db` to refresh golden answers.
- Free OpenRouter models hit daily/minute limits during batch `--live` runs; UI chat with gemma works for demos.
