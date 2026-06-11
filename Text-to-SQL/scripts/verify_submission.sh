#!/usr/bin/env bash
# Run all local verification steps (no LLM). Pass absolute DB path.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DB="${1:-}"

if [[ -z "$DB" ]]; then
  echo "Usage: $0 /absolute/path/to/blockchain.db"
  exit 1
fi

cd "$ROOT"
echo "=== check_node.py (§1) ==="
python3 check_node.py || echo "WARN: bitcoind not reachable"

echo ""
echo "=== validate.py (§3d) ==="
python3 validate.py --db "$DB"

echo ""
echo "=== run_tests.py golden tests (§5–§6) ==="
python3 run_tests.py --db "$DB"

echo ""
echo "=== Done. For LLM tests (§4–§6 live), run: ==="
echo "  export OPENROUTER_API_KEY=your_key"
echo "  python3 run_tests.py --db \"$DB\" --live"
echo "  python3 capture_live_hard.py --db \"$DB\" --write"
