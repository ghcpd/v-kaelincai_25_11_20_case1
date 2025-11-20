#!/usr/bin/env bash
set -euo pipefail
./setup.sh
source .venv/bin/activate
pytest -q

echo "Enhanced Ticket UI tests finished. Results in results/"
