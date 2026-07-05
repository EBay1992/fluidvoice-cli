#!/usr/bin/env bash
# Install fluidvoice CLI globally from the built wheel.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 -m pip install --upgrade pip build
python3 -m build
python3 -m pip install --force-reinstall "$ROOT/dist"/fluidvoice_cli-*.whl

echo ""
echo "Installed: $(fluidvoice --version)"
echo "Try: fluidvoice doctor"
