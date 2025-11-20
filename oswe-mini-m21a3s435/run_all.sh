#!/usr/bin/env bash
set -euo pipefail

ROOT=$(pwd)
mkdir -p results

echo "Running Case1 - Baseline Report Service"
bash "$ROOT/Project_A_BaselineReportService/run_tests.sh" || true

echo "Running Case1 - Enhanced Report Service"
bash "$ROOT/Project_B_EnhancedReportService/run_tests.sh" || true

echo "Running Case2 - Baseline Ticket UI"
bash "$ROOT/Project_A_BaselineTicketUI/run_tests.sh" || true

echo "Running Case2 - Enhanced Ticket UI"
bash "$ROOT/Project_B_EnhancedTicketUI/run_tests.sh" || true

# Collect results into root results/
rm -rf results/* || true
mkdir -p results/ReportService/baseline
mkdir -p results/ReportService/enhanced
mkdir -p results/TicketUI/baseline
mkdir -p results/TicketUI/enhanced

cp -R Project_A_BaselineReportService/results/* results/ReportService/baseline/ 2>/dev/null || true
cp -R Project_B_EnhancedReportService/results/* results/ReportService/enhanced/ 2>/dev/null || true
cp -R Project_A_BaselineTicketUI/results/* results/TicketUI/baseline/ 2>/dev/null || true
cp -R Project_B_EnhancedTicketUI/results/* results/TicketUI/enhanced/ 2>/dev/null || true

echo "Aggregating and generating compare_report.md"
python3 scripts/aggregate_results.py

echo "All runs complete. Results are in ./results and compare_report.md"
