#!/usr/bin/env bash
# One-time setup: venv + pip deps (run interactively in WSL).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! python3 -m venv --help >/dev/null 2>&1; then
  echo "Installing python3-venv (requires sudo password)..."
  sudo apt update
  sudo apt install -y python3-venv python3-pip
fi

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Done. Before running LLM scripts:"
echo "  source .venv/bin/activate"
echo "  export OPENROUTER_API_KEY=your_key"
