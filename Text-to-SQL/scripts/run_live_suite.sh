#!/usr/bin/env bash
# §4/§5/§6 live LLM tests + hard-case capture (requires OPENROUTER_API_KEY).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DB="${1:-$HOME/hw3-data/blockchain.db}"

cd "$ROOT"
if [[ -z "${OPENROUTER_API_KEY:-}" ]] && [[ ! -f "$ROOT/.env" ]]; then
  echo "ERROR: set OPENROUTER_API_KEY in .env or export it"
  exit 1
fi
source .venv/bin/activate 2>/dev/null || true

python3 run_tests.py --db "$DB" --live | tee logs/live_tests.log
python3 capture_live_hard.py --db "$DB" --write | tee -a logs/live_tests.log

echo "Results also in tests/LIVE_LLM_RESULTS.md (update manually or re-run)."
