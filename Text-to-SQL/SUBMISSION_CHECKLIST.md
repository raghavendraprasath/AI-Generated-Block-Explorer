# Homework 3 — Submission Checklist

## Done in repo

- [x] §2 Schema + ingest + validate + updater
- [x] §2a Approach 1 + Approach 2
- [x] §3b deterministic ingest + §3c cron (`install_cron.sh`, `logs/cron.log`)
- [x] §3d proof log (`logs/submission_proof.txt`)
- [x] §4 `text_to_sql.py` + web UI + CLI chat
- [x] §5 twelve test triples + golden tests **12/12** (answers synced to 110k-block DB)
- [x] §6 three hard failures + slide
- [x] Notes: Ethereum, pricing, charts, CANNOT_ANSWER
- [x] Screenshots in `screenshots/` (01–09, 08 chart)
- [x] `tests/LIVE_LLM_RESULTS.md` (honest partial live scores + rate-limit note)

## Regenerate evidence (optional)

```bash
cd /mnt/c/Users/adity/Desktop/INFO7500/AI-Generated-Block-Explorer/Text-to-SQL
source .venv/bin/activate

# After updater grows the DB, refresh golden answers:
python3 scripts/refresh_test_answers.py ~/hw3-data/blockchain.db

# Proof + screenshots:
./scripts/generate_submission_proof.sh ~/hw3-data/blockchain.db
python3 scripts/generate_submission_screenshots.py --db ~/hw3-data/blockchain.db

# Live LLM (when OpenRouter quota available):
./scripts/run_live_suite.sh ~/hw3-data/blockchain.db
```

## Replace mock chat screenshot (optional)

`screenshots/07_chat.png` is a rendered mock. Replace with your browser capture of the Streamlit UI for a polished submission.

## Git

```bash
cd /mnt/c/Users/adity/Desktop/INFO7500/AI-Generated-Block-Explorer
git add Text-to-SQL/
git status   # confirm blockchain.db and .env NOT staged
git commit -m "Add Homework 3 Text-to-SQL deliverables"
```
