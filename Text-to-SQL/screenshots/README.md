# Screenshot guide — Homework 3

Take **real** screenshots from your terminal and browser. Do not use auto-generated PNGs.

## Quick start

```bash
cd Text-to-SQL
source .venv/bin/activate
chmod +x scripts/demo_for_screenshots.sh
./scripts/demo_for_screenshots.sh ~/hw3-data/blockchain.db
```

The script runs each command and pauses so you can capture the screen. Save files in this folder.

---

## Essential screenshots (minimum set)

| File | What to capture | How |
|------|-----------------|-----|
| `01_bitcoind_rpc.png` | `getblockcount`, `getblockchaininfo`, `getblock` on chain tip | Terminal: `python3 check_node.py` |
| `02_validate.png` | `Validation passed.` | Terminal: `python3 validate.py --db ~/hw3-data/blockchain.db` |
| `03_text_to_sql.png` | Question → SQL → answer | Terminal: `python3 text_to_sql.py --question "How many blocks are in the database?" --db ~/hw3-data/blockchain.db` |
| `04_run_tests.png` | `12 passed, 0 failed` | Terminal: `python3 run_tests.py --db ~/hw3-data/blockchain.db --standard-only` |
| `05_ui_home.png` | Block Explorer AI — Home chat with SQL + answer | Browser: `./scripts/run_web_ui.sh ~/hw3-data/blockchain.db` → http://localhost:8501 |
| `06_ui_insights.png` | Insights page with a rendered chart | Same app → **Insights** → Quick views → Render chart |
| `07_cron_log.png` | Updater/cron log lines | Terminal: `tail -30 logs/cron.log` |

---

## Optional (bonus / extra credit evidence)

| File | What to capture |
|------|-----------------|
| `08_schema_generate.png` | `generate_schema.py` output + head of `schema_generated.sql` |
| `09_run_tests_live.png` | `python3 run_tests.py --db ... --live` (honest partial score OK) |
| `10_chart.png` | CLI chart or second Insights chart |

---

## Class presentation (Hard failures)

Not a screenshot — submit/open the slide deck:

```bash
# Open in browser (Chrome/Edge), present with F11 fullscreen
slides/hard_failures.html
```

Screenshot optional: `08_hard_failures_slide.png` if your course wants a static slide image.

---

## Tips

- Use **WSL terminal** at a comfortable font size; avoid Cursor embedded terminal if you want a natural look.
- Use **system browser** (Chrome/Edge), not Cursor’s preview, for UI shots.
- Database path: `~/hw3-data/blockchain.db` (not `/mnt/c/...`).
- Refresh test answers after DB grows: `python3 scripts/refresh_test_answers.py ~/hw3-data/blockchain.db`
