#!/usr/bin/env bash
# Launch Streamlit web chat UI.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DB="${1:-${HW3_DB_PATH:-$HOME/hw3-data/blockchain.db}}"

cd "$ROOT"
# .env is loaded automatically by web_ui.py via python-dotenv
if [[ -z "${OPENROUTER_API_KEY:-}" ]] && [[ ! -f "$ROOT/.env" ]]; then
  echo "ERROR: set OPENROUTER_API_KEY in .env or export it"
  echo "  cp .env.example .env   # then edit .env"
  exit 1
fi
source .venv/bin/activate 2>/dev/null || true
export HW3_DB_PATH="$DB"

echo "Open http://localhost:8501 in your browser"
exec streamlit run web_ui.py --server.headless true
