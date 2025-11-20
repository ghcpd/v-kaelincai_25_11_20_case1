#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "Running baseline (Project A)..."
bash "$ROOT/Project_A_BaselineTicketUI/run_tests.sh"

echo "Running enhanced (Project B)..."
bash "$ROOT/Project_B_EnhancedTicketUI/run_tests.sh"

echo "Aggregating results..."
python "$ROOT/scripts/aggregate_results.py"

echo "Done. See results/compare_report.md"
