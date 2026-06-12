# Homework 3 — Submission deliverables

What to submit for **Homework 3: Text-to-SQL** (INFO7500).

---

## Code & documentation (repository)

| Deliverable | Location |
|-------------|----------|
| SQLite schema (getblock verbosity=2) | `schema.sql` |
| Schema auto-generation bonus | `prompts/run_approach1.py`, `generate_schema.py`, `prompts/` docs |
| Ingestion (RPC → DB) | `ingest.py` |
| Updater + cron | `updater.py`, `scripts/install_cron.sh`, `crontab.example` |
| Validation | `validate.py` |
| Text-to-SQL | `text_to_sql.py` (evolved from HW2) |
| Test cases (≥10 triples) | `tests/test_cases.json`, `run_tests.py` |
| Hard failure cases (3) | `tests/hard_failures.json` |
| Class slides | `slides/hard_failures.html` |
| Notes: Ethereum, pricing, chat, charts | `schema_extensions.sql`, `ingest_extensions.py`, `Home.py`, `charts.py` |
| CANNOT_ANSWER tests | `tests/cannot_answer_cases.json` |
| README | `README.md` |

**Do not commit:** `blockchain.db`, `.env`, `logs/`, `.venv/`

---

## Runtime evidence (screenshots)

Capture manually — see `screenshots/README.md` and run:

```bash
./scripts/demo_for_screenshots.sh ~/hw3-data/blockchain.db
```

**Essential (7):**

1. `01_bitcoind_rpc.png` — `check_node.py`
2. `02_validate.png` — validate passed
3. `03_text_to_sql.png` — NL → SQL → answer
4. `04_run_tests.png` — 12/12 golden tests
5. `05_ui_home.png` — Streamlit Home chat
6. `06_ui_insights.png` — Streamlit chart
7. `07_cron_log.png` — updater/cron log

**Optional:** schema generation, live LLM tests, extra charts

---

## Prerequisites from Homework 2 (already submitted separately)

HW3 builds on HW2 tooling (separate folder `Tooling-for-AI-Generated-Block-Explorer/`):

- Docker (`Dockerfile`, `hello_docker.py`)
- bitcoind built and RPC working
- OpenAI/OpenRouter text-to-sql prototype (`text_to_sql.py`)

HW3 does **not** re-submit HW2 files unless your instructor asks for one combined repo.

---

## Before you submit

- [ ] `python3 run_tests.py --db ~/hw3-data/blockchain.db --standard-only` → 12/12
- [ ] `python3 validate.py --db ~/hw3-data/blockchain.db` → passed
- [ ] Refresh answers if DB grew: `scripts/refresh_test_answers.py`, `scripts/refresh_hard_failures.py`
- [ ] Screenshots saved in `screenshots/`
- [ ] Open `slides/hard_failures.html` in browser for class presentation
- [ ] Git commit `Text-to-SQL/` (no secrets, no database)
