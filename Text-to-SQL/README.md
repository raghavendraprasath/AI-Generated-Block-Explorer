# Homework 3: Text-to-SQL — Bitcoin Block Explorer

**INFO7500 – Cryptocurrency and Smart Contracts**  
**Student:** Raghavendra Prasath Sridhar

Natural-language questions → SQLite queries over Bitcoin blockchain data ingested from `bitcoind` RPC.

> **Note:** The assignment refers to “getblocks”; Bitcoin Core uses **`getblock(blockhash, 2)`** (verbosity=2) for full block + transaction JSON.

---

## Repository layout

```
Text-to-SQL/
├── schema.sql                 # Final normalized Bitcoin schema
├── schema_extensions.sql      # Ethereum + BTC price tables (Notes)
├── schema_generated.sql       # Approach 2 auto-draft
├── generate_schema.py         # Approach 2 generator
├── ingest.py                  # Deterministic RPC → SQLite (100% correct)
├── ingest_extensions.py       # Load Ethereum + pricing samples
├── validate.py                # Consistency checks
├── updater.py                 # Ingest + extensions + validate (for cron)
├── crontab.example            # Schedule every 5 minutes
├── check_node.py              # getblockcount / getblockchaininfo
├── text_to_sql.py             # NL → SQL → answer
├── chat.py                    # CLI chat UI
├── web_ui.py                  # Streamlit web chat UI
├── charts.py                  # Chart generation from queries
├── run_tests.py               # Test suite
├── capture_live_hard.py       # Capture live LLM hard-failure outputs
├── tests/                     # test_cases, hard_failures, cannot_answer
├── slides/hard_test_cases.md  # Class presentation
├── prompts/                   # Schema + ingest LLM documentation
└── examples/                  # getblock JSON samples
```

`blockchain.db` (~500MB) is **gitignored** — build locally with `ingest.py`.

---

## Setup

```bash
cd Text-to-SQL
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
**API key (one-time setup — recommended):**

```bash
cp .env.example .env
# Edit .env and set OPENROUTER_API_KEY=sk-or-v1-...
```

All scripts (`text_to_sql.py`, `chat.py`, `web_ui.py`, `run_tests.py --live`) load `.env` automatically.  
Alternative: `export OPENROUTER_API_KEY=...` in `~/.bashrc` for every shell.
```

### bitcoind (§1)

```bash
# WSL — after building Bitcoin Core
./build/bin/bitcoind -daemon
python3 check_node.py              # getblockcount, getblockchaininfo
```

Sync ~100,000+ blocks (or until disk limit). Node should keep running for new blocks.

---

## §2 Schema

**Final schema:** `schema.sql` — blocks, transactions, vin, vout, coinbase, sync_state, `txinwitness`.

### Bonus §2a — Two auto-generation approaches

| Approach | Command | Output |
|----------|---------|--------|
| **1 — LLM → SQL** | `python3 prompts/run_approach1.py` | `prompts/schema_llm_direct.sql` |
| **2 — Code → SQL** | `python3 generate_schema.py examples/getblock_100000.json schema_generated.sql` | `schema_generated.sql` |

See `prompts/schema_llm_prompt.md` for limitations and manual fixes → `schema.sql`.

---

## §3 Updater + consistency

### Initial ingest (100k blocks)

```bash
python3 ingest.py --db /absolute/path/to/blockchain.db --start 0 --end 100000
python3 ingest_extensions.py --db /absolute/path/to/blockchain.db
python3 validate.py --db /absolute/path/to/blockchain.db
```

### Scheduled updates (every few minutes)

```bash
python3 updater.py --db /absolute/path/to/blockchain.db
# Cron: see crontab.example (*/5 * * * *)
```

### Bonus §3b — 100% correct ingestion

We **document** LLM ingestion (`prompts/ingest_llm_prompt.md`) but use **deterministic `ingest.py`** at runtime for guaranteed correctness. `validate.py` checks height continuity, `ntx` counts, FK orphans, and optional RPC tip.

---

## §4 Text-to-SQL

```bash
python3 text_to_sql.py \
  --question "How many blocks are in the database?" \
  --db /absolute/path/to/blockchain.db
```

- **System prompt (§4c.i):** exact assignment text in `text_to_sql.CORE_SYSTEM_PROMPT`
- **Schema:** auto-loaded from `sqlite_master`
- **User message:** schema + question instance
- **Notes:** `CANNOT_ANSWER` for unanswerable questions (live API, unrelated domains)

### Chat UI (Notes)

**Web UI (recommended for screenshots):**

```bash
export OPENROUTER_API_KEY=your_key
./scripts/run_web_ui.sh ~/hw3-data/blockchain.db
# Open http://localhost:8501
```

**CLI chat:**

```bash
python3 chat.py --db /absolute/path/to/blockchain.db
```

### Charts (Notes)

```bash
python3 charts.py \
  --question "SELECT block_height, COUNT(*) FROM transactions GROUP BY block_height ORDER BY block_height LIMIT 50" \
  --db /absolute/path/to/blockchain.db \
  --output charts/blocks_tx_count.png
```

Or use a natural-language question that returns 1–2 columns.

---

## §5–§6 Tests

```bash
# Golden SQL tests (no API key needed)
python3 run_tests.py --db /absolute/path/to/blockchain.db

# Live LLM tests (CANNOT_ANSWER + optional LLM accuracy)
python3 run_tests.py --db /absolute/path/to/blockchain.db --live

# Capture live incorrect SQL for hard cases
python3 capture_live_hard.py --db /absolute/path/to/blockchain.db --write
```

| File | Purpose |
|------|---------|
| `tests/test_cases.json` | 12 standard triples (question, SQL, answer) |
| `tests/hard_failures.json` | 3 hard cases with expected + incorrect SQL/answers |
| `tests/cannot_answer_cases.json` | Questions that must return `CANNOT_ANSWER` |
| `tests/extension_cases.json` | Ethereum + pricing queries |
| `slides/hard_test_cases.md` | Class slide (SpiderV2 reference) |

---

## Notes — Extensions

| Feature | Implementation |
|---------|----------------|
| **Ethereum** | `ethereum_blocks` table + `examples/eth_block_sample.json` |
| **BTC pricing** | `btc_daily_prices` table + `examples/btc_prices_sample.json` |
| **CANNOT_ANSWER** | `text_to_sql.py` + `tests/cannot_answer_cases.json` |
| **Chat UI** | `web_ui.py` (Streamlit) + `chat.py` (CLI) |
| **Charts** | `charts.py` (matplotlib) |

Live CoinGecko / full Ethereum sync are **out of scope**; the schema supports extensions and the LLM rejects live/unavailable data.

---

## Database stats (reference)

After ingesting blocks 0–100,000:

| Metric | Value |
|--------|-------|
| Blocks | 100,001 |
| Transactions | 216,575 |
| Max height | 100,000 |

---

## Submission

**Full checklist:** `SUBMISSION_CHECKLIST.md`  
**WSL database:** use `~/hw3-data/blockchain.db` (not `/mnt/c/...` — avoids disk I/O errors)  
**Proof script:** `./scripts/generate_submission_proof.sh ~/hw3-data/blockchain.db`  
**Live LLM:** `./scripts/run_live_suite.sh ~/hw3-data/blockchain.db`

## Screenshots checklist

1. `check_node.py` — `getblockcount` / `getblockchaininfo` / `getblock` on tip
2. `generate_schema.py` output / `schema_generated.sql`
3. `ingest.py` progress through block 100,000
4. `validate.py` passing
5. `text_to_sql.py` sample Q&A
6. `run_tests.py` all passing
7. `chat.py` session
8. `charts.py` output PNG

---

## References

- [Bitcoin RPC reference](https://developer.bitcoin.org/reference/rpc/index.html)
- [Prompt engineering guide](https://www.promptingguide.ai/)
- [Spider 2.0 Text-to-SQL leaderboard](https://spider2-sql.github.io/)
