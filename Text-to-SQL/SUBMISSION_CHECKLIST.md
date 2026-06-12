# Homework 3 — Pre-submit checklist

## Done in repo

- [x] Schema + ingest + validate + updater
- [x] Schema auto-generation bonus (Approach 1 + 2)
- [x] Cron updater (`install_cron.sh`, `logs/cron.log`)
- [x] Text-to-SQL + Block Explorer AI UI (Home · Insights · Samples)
- [x] 12 golden test triples
- [x] 3 hard failures + HTML slide deck
- [x] Notes: Ethereum, pricing, charts, CANNOT_ANSWER

## Your actions

1. **Screenshots** — `./scripts/demo_for_screenshots.sh ~/hw3-data/blockchain.db`  
   See `screenshots/README.md`

2. **Refresh DB-dependent answers** (if updater added blocks):
   ```bash
   python3 scripts/refresh_test_answers.py ~/hw3-data/blockchain.db
   python3 scripts/refresh_hard_failures.py ~/hw3-data/blockchain.db
   ```

3. **Presentation** — open `slides/hard_failures.html` in browser (F11 fullscreen)

4. **Proof log** (optional): `./scripts/generate_submission_proof.sh ~/hw3-data/blockchain.db`

5. **Git commit** — see `SUBMISSION.md`

## Final step

Update **`README.md`** after screenshots and any last code changes so it reflects the final state of the project.
