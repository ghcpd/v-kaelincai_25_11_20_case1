#!/usr/bin/env bash
set -e
# Run baseline report tests
pushd Project_A_BaselineReportService
./run_tests.sh || true
popd
# Run enhanced report tests
pushd Project_B_EnhancedReportService
./run_tests.sh || true
popd
# Run baseline UI tests
pushd Project_A_BaselineTicketUI
./run_tests.sh || true
popd
# Run enhanced UI tests
pushd Project_B_EnhancedTicketUI
./run_tests.sh || true
popd
# Collect results
mkdir -p results
cp Project_A_BaselineReportService/results/* results/ 2>/dev/null || true
cp Project_B_EnhancedReportService/results/* results/ 2>/dev/null || true
cp Project_A_BaselineTicketUI/results/* results/ 2>/dev/null || true
cp Project_B_EnhancedTicketUI/results/* results/ 2>/dev/null || true
