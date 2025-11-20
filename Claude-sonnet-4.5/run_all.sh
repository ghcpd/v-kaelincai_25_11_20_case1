#!/bin/bash
# Master test execution script - runs both projects and generates comparison

echo "=============================================================================="
echo "SAAS TICKET DETAIL PAGE UI/UX IMPROVEMENT - EVALUATION SUITE"
echo "=============================================================================="
echo ""

# Run Project A - Baseline
echo ""
echo "=============================================================================="
echo "PHASE 1: Running Baseline Ticket UI (Project A)"
echo "=============================================================================="
cd Project_A_BaselineTicketUI
bash run_tests.sh
cd ..

# Run Project B - Enhanced
echo ""
echo "=============================================================================="
echo "PHASE 2: Running Enhanced Ticket UI (Project B)"
echo "=============================================================================="
cd Project_B_EnhancedTicketUI
bash run_tests.sh
cd ..

# Copy results to central location
echo ""
echo "=============================================================================="
echo "PHASE 3: Aggregating Results"
echo "=============================================================================="
mkdir -p results
cp Project_A_BaselineTicketUI/results/results_pre.json results/
cp Project_A_BaselineTicketUI/results/log_pre.txt results/
cp Project_B_EnhancedTicketUI/results/results_post.json results/
cp Project_B_EnhancedTicketUI/results/log_post.txt results/

echo "Results aggregated in: results/"

# Generate comparison report
echo ""
echo "=============================================================================="
echo "PHASE 4: Generating Comparison Report"
echo "=============================================================================="
python generate_comparison_report.py

echo ""
echo "=============================================================================="
echo "ALL TESTS COMPLETE"
echo "=============================================================================="
echo ""
echo "Review the following files:"
echo "  - results/results_pre.json  (Baseline results)"
echo "  - results/results_post.json (Enhanced results)"
echo "  - results/compare_report.md (Comparison analysis)"
echo ""
