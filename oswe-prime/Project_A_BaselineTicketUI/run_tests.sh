#!/bin/bash
set -e
ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
export SCENARIO_PATH="$ROOT_DIR/../shared/test_scenarios.json"
export OUTPUT_DIR="$ROOT_DIR/results"
python -m pytest -q
# Run harness to generate results and logs
python "$ROOT_DIR/src/harness.py"
