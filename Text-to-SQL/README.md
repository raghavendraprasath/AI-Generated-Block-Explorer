# Homework 3: Text-to-SQL — Block Explorer AI

**INFO7500 – Cryptocurrency and Smart Contracts**  
**Student:** Raghavendra Prasath Sridhar

Natural-language questions → SQLite queries over Bitcoin blockchain data ingested from `bitcoind` RPC.

> Bitcoin Core uses **`getblock(blockhash, 2)`** (verbosity=2) for full block + transaction JSON. The assignment text sometimes says “getblocks”; this project uses `getblock`.

**Evolved from Homework 2:** `Tooling-for-AI-Generated-Block-Explorer/text_to_sql.py` (OpenRouter prototype) → `text_to_sql.py` with live schema, CLI, and SQL execution.

---

## Repository layout

```
Text-to-SQL/
├── schema.sql                 # Final normalized Bitcoin schema
├── schema_extensions.sql      # Ethereum + BTC price tables
├── schema_generated.sql       # Approach 2 auto-draft
├── generate_schema.py         # Approach 2 generator
├── ingest.py                  # Deterministic RPC → SQLite
├── ingest_extensions.py       # Ethereum + pricing samples
├── validate.py                # Consistency checks
├── updater.py                 # Ingest + extensions + validate
├── check_node.py              # getblockcount / getblockchaininfo
├── text_to_sql.py             # NL → SQL → answer
├── chat.py                    # CLI chat
├── Home.py                    # Streamlit app (entry point)
├── web_ui.py                  # Shim → Home.py
├── pages/                     # Insights · Samples
├── charts.py                  # Matplotlib charts
├── run_tests.py               # Test suite
├── tests/                     # test_cases, hard_failures, cannot_answer
├── slides/hard_failures.html  # Class presentation (open in browser)
├── scripts/                   # setup, cron, screenshot demo, proof
├── prompts/                   # Schema + ingest LLM documentation
├── screenshots/               # Your manual submission PNGs
├── SUBMISSION.md              # Full deliverables list
└── examples/                  # getblock JSON samples
```

`blockchain.db` (~500MB+) is **gitignored**. Build locally or copy to `~/hw3-data/blockchain.db` on WSL.

---

## Setup

```bash
cd Text-to-SQL
python3 -m venv .venv
source .venv/bin/activate          # Windows WSL recommended
pip install -r requirements.txt

cp .env.example .env
# Edit .env: OPENROUTER_API_KEY=sk-or-v1-...
```

All LLM scripts load `.env` automatically via `project_env.py`.

### bitcoind

```bash
./build/bin/bitcoind -daemon       # from HW2 Bitcoin Core build
python3 check_node.py              # getblockcount, getblockchaininfo, getblock
```

Sync ~100,000+ blocks. Keep the node running for the updater.

### Database (WSL — recommended)

```bash
mkdir -p ~/hw3-data
cp /path/to/blockchain.db ~/hw3-data/   # or ingest fresh
python3 ingest_extensions.py --db ~/hw3-data/blockchain.db
```

Use `~/hw3-data/blockchain.db` everywhere — avoid `/mnt/c/...` (SQLite disk I/O errors).

---

## Part 1 — bitcoind sync

- **110k+ blocks** synced in our environment
- Proof: `python3 check_node.py` or `./scripts/generate_submission_proof.sh ~/hw3-data/blockchain.db`

---

## Part 2 — Schema

**Final schema:** `schema.sql` — blocks, transactions, inputs, outputs, coinbase, sync_state, txinwitness.

### Bonus — auto-generate schema from JSON

| Approach | Command | Output |
|----------|---------|--------|
| LLM → SQL directly | `python3 prompts/run_approach1.py` | `prompts/schema_llm_direct.sql` |
| Code → SQL | `python3 generate_schema.py examples/getblock_100000.json schema_generated.sql` | `schema_generated.sql` |

See `prompts/schema_llm_prompt.md` and `prompts/prompt_engineering_examples.md` for limitations and manual fixes → `schema.sql`.

---

## Part 3 — Updater & consistency

```bash
# Initial ingest
python3 ingest.py --db ~/hw3-data/blockchain.db --start 0 --end 100000
python3 ingest_extensions.py --db ~/hw3-data/blockchain.db
python3 validate.py --db ~/hw3-data/blockchain.db

# Manual update
python3 updater.py --db ~/hw3-data/blockchain.db

# Cron (every 5 min)
./scripts/install_cron.sh ~/hw3-data/blockchain.db
```

**Bonus ingestion:** LLM approach documented in `prompts/ingest_llm_prompt.md`; production uses deterministic `ingest.py` for 100% correctness.

`validate.py` checks height continuity, `ntx` counts, foreign keys, and optional RPC tip cross-check.

---

## Part 4 — Text-to-SQL

```bash
python3 text_to_sql.py \
  --question "How many blocks are in the database?" \
  --db ~/hw3-data/blockchain.db
```

- **System prompt:** exact assignment text in `text_to_sql.CORE_SYSTEM_PROMPT`
- **Schema:** loaded from `sqlite_master` into the user message
- **CANNOT_ANSWER:** for unanswerable questions (live API, unrelated domains)

### Block Explorer AI (Streamlit)

```bash
./scripts/run_web_ui.sh ~/hw3-data/blockchain.db
# Open http://localhost:8501 in your system browser
```

| Page | Purpose |
|------|---------|
| **Home** | Natural-language chat |
| **Insights** | Charts from queries |
| **Samples** | Curated test questions |

CLI alternative: `python3 chat.py --db ~/hw3-data/blockchain.db`

### Charts

```bash
python3 charts.py \
  --question "Heights and tx counts for first 20 blocks" \
  --db ~/hw3-data/blockchain.db \
  --sql "SELECT height, ntx FROM blocks ORDER BY height ASC LIMIT 20" \
  --output charts/output.png
```

Or use the **Insights** page in the web app.

---

## Part 5 & 6 — Tests

```bash
# Golden SQL tests (no API key)
python3 run_tests.py --db ~/hw3-data/blockchain.db --standard-only

# Live LLM (optional)
python3 run_tests.py --db ~/hw3-data/blockchain.db --live
python3 capture_live_hard.py --db ~/hw3-data/blockchain.db --write
```

| File | Purpose |
|------|---------|
| `tests/test_cases.json` | 12 standard triples (question, SQL, answer) |
| `tests/hard_failures.json` | 3 hard cases with expected + incorrect SQL/answers |
| `tests/cannot_answer_cases.json` | Must return `CANNOT_ANSWER` |
| `tests/extension_cases.json` | Ethereum + pricing |
| `tests/LIVE_LLM_RESULTS.md` | Honest live LLM scores |
| `slides/hard_failures.html` | Class presentation — arrow keys, F11 fullscreen |

Refresh answers after DB grows:

```bash
python3 scripts/refresh_test_answers.py ~/hw3-data/blockchain.db
python3 scripts/refresh_hard_failures.py ~/hw3-data/blockchain.db
```

---

## Notes — Extensions

| Feature | Implementation |
|---------|----------------|
| Ethereum | `ethereum_blocks` + `examples/eth_block_sample.json` |
| BTC pricing | `btc_daily_prices` + `examples/btc_prices_sample.json` |
| CANNOT_ANSWER | `text_to_sql.py` + `tests/cannot_answer_cases.json` |
| Chat UI | `Home.py` + `chat.py` |
| Charts | `charts.py` + Insights page |

---

## Screenshots & submission

**Do not use auto-generated PNGs.** Capture your own:

```bash
chmod +x scripts/demo_for_screenshots.sh
./scripts/demo_for_screenshots.sh ~/hw3-data/blockchain.db
```

Essential shots listed in `screenshots/README.md` (7 terminal + browser captures).

**Full deliverables:** `SUBMISSION.md`  
**Pre-submit checklist:** `SUBMISSION_CHECKLIST.md`

---

## References

- [Bitcoin RPC reference](https://developer.bitcoin.org/reference/rpc/index.html)
- [Prompt engineering guide](https://www.promptingguide.ai/)
- [Spider 2.0 Text-to-SQL leaderboard](https://spider2-sql.github.io/)
