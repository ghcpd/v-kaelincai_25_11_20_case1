#!/usr/bin/env bash
set -e
ROOT=$(pwd)
echo "Running all project tests and aggregating results"

echo "-> Running Project A (baseline)"
pushd Project_A_BaselineTicketUI >/dev/null
./run_tests.sh
popd >/dev/null

echo "-> Running Project B (enhanced)"
pushd Project_B_EnhancedTicketUI >/dev/null
./run_tests.sh
popd >/dev/null

mkdir -p results

echo "Collecting results into root results/"
cp Project_A_BaselineTicketUI/results/results_pre.json results/results_pre.json || true
cp Project_A_BaselineTicketUI/results/log_pre.txt results/log_pre.txt || true
cp Project_A_BaselineTicketUI/results/summary_pre.json results/summary_pre.json || true

cp Project_B_EnhancedTicketUI/results/results_post.json results/results_post.json || true
cp Project_B_EnhancedTicketUI/results/log_post.txt results/log_post.txt || true
cp Project_B_EnhancedTicketUI/results/summary_post.json results/summary_post.json || true

# copy preview artifacts
cp Project_A_BaselineTicketUI/results/baseline_preview.html results/ || true
cp Project_B_EnhancedTicketUI/results/enhanced_preview.html results/ || true

echo "Generating compare report"
python compare_results.py

echo "Aggregation complete. See results/ and compare_report.md"
