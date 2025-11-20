#!/usr/bin/env bash
set -euo pipefail
./setup.sh
source .venv/bin/activate
pytest -q

echo "Baseline Ticket UI tests finished: results in results/"
