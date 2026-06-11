#!/usr/bin/env bash
# Generate §1 + §3d proof log (no API key required).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DB="${1:-$HOME/hw3-data/blockchain.db}"
LOG="$ROOT/logs/submission_proof.txt"
mkdir -p "$ROOT/logs"

{
  echo "=== Homework 3 Submission Proof ==="
  echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "Database: $DB"
  echo ""
  echo "=== §1 bitcoind RPC (check_node.py) ==="
  cd "$ROOT" && python3 check_node.py || echo "WARN: bitcoind not reachable"
  echo ""
  echo "=== §3d validate.py ==="
  python3 validate.py --db "$DB" || true
  echo ""
  echo "=== §5 golden tests (no LLM) ==="
  python3 run_tests.py --db "$DB" --standard-only || true
} | tee "$LOG"

echo ""
echo "Wrote $LOG"
echo "Screenshot this file for §1/§3d evidence."
