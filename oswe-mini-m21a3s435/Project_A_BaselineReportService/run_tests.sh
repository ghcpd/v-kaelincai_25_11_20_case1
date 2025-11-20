#!/usr/bin/env bash
set -euo pipefail
./setup.sh
source .venv/bin/activate
pytest -q

echo "Test run complete. Results are in results/"
