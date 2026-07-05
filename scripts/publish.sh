#!/usr/bin/env bash
# Build distribution artifacts for PyPI upload.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install --upgrade build twine
python3 -m build
echo ""
echo "Built:"
ls -la dist/
echo ""
echo "Test upload:  twine upload --repository testpypi dist/*"
echo "Production:   twine upload dist/*"
