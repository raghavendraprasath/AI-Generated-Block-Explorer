# Screenshots for Homework 3 submission

Capture these and save PNGs in this folder.

**Automated:** run `python3 scripts/generate_submission_screenshots.py --db ~/hw3-data/blockchain.db` to render terminal-style PNGs from command output.

| File | Command |
|------|---------|
| `01_bitcoind_rpc.png` | `python3 check_node.py` — shows `getblockcount`, `getblockchaininfo`, `getblock` on tip |
| `02_schema_generate.png` | `python3 generate_schema.py examples/getblock_100000.json schema_generated.sql && head -20 schema_generated.sql` |
| `03_ingest_complete.png` | `python3 validate.py --db /path/to/blockchain.db` — "Validation passed" |
| `04_text_to_sql.png` | `python3 text_to_sql.py --question "How many blocks are in the database?" --db /path/to/blockchain.db` |
| `05_run_tests.png` | `python3 run_tests.py --db /path/to/blockchain.db` — 12/12 pass |
| `06_run_tests_live.png` | `python3 run_tests.py --db /path/to/blockchain.db --live` |
| `07_chat.png` | Web UI: `./scripts/run_web_ui.sh ~/hw3-data/blockchain.db` → ask a question in browser (or CLI `chat.py`) |
| `07b_web_ui.png` | Optional: full browser window showing Streamlit chat |
| `08_chart.png` | `python3 charts.py --question "..." --db /path/to/blockchain.db --output screenshots/chart.png` |
| `09_cron_log.png` | `tail logs/cron.log` or `logs/updater.log` after cron runs |
