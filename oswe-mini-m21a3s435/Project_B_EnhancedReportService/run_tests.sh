#!/usr/bin/env bash
set -euo pipefail
./setup.sh
source .venv/bin/activate
pytest -q

echo "Enhanced report service tests finished. Results are in results/"
