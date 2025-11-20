#!/bin/bash
set -e
ROOT=$(cd "$(dirname "$0")" && pwd)

echo "Running Project A Baseline Tests..."
(cd "$ROOT/Project_A_BaselineTicketUI" && bash ./run_tests.sh)

echo "Running Project B Enhanced Tests..."
(cd "$ROOT/Project_B_EnhancedTicketUI" && bash ./run_tests.sh)

# aggregate
mkdir -p "$ROOT/results"
cp Project_A_BaselineTicketUI/results/results_pre.json "$ROOT/results/" 2>/dev/null || true
cp Project_A_BaselineTicketUI/results/log_pre.txt "$ROOT/results/" 2>/dev/null || true
cp Project_B_EnhancedTicketUI/results/results_post.json "$ROOT/results/" 2>/dev/null || true
cp Project_B_EnhancedTicketUI/results/log_post.txt "$ROOT/results/" 2>/dev/null || true

# Generate compare report
python3 "$ROOT/compare_results.py" "$ROOT/results/results_pre.json" "$ROOT/results/results_post.json" "$ROOT/results/compare_report.md"

echo "All done. Reports are in $ROOT/results"
