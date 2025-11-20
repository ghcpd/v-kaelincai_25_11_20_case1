#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$PROJECT_ROOT/setup.sh"
VENV_DIR="$PROJECT_ROOT/.venv"
if [ -d "$VENV_DIR/Scripts" ]; then
  PYTHON_BIN="$VENV_DIR/Scripts/python"
else
  PYTHON_BIN="$VENV_DIR/bin/python"
fi
export TEST_SCENARIOS_PATH="$PROJECT_ROOT/../test_scenarios.json"
export RESULTS_DIR="$PROJECT_ROOT/results"
export LOG_DIR="$PROJECT_ROOT/logs"
export PROJECT_EXPECTATION_KEY="baseline"
export RESULT_KIND="pre"
mkdir -p "$RESULTS_DIR" "$LOG_DIR"
"$PYTHON_BIN" -m pytest "$PROJECT_ROOT/tests" -q
