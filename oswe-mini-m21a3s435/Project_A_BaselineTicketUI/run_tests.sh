#!/usr/bin/env bash
set -e
ROOT_DIR=$(pwd)
echo "Running Project A baseline tests..."
python -m pytest -q

# Prepare results directory and evaluate scenarios
mkdir -p results
python -u -c "from src.evaluator import evaluate_all;import os;print('Evaluating scenarios...');evaluate_all(os.path.abspath('../test_scenarios.json'), os.path.abspath('results'))"

# Generate a simple HTML artifact to visualize baseline
cat > results/baseline_preview.html <<'HTML'
<!doctype html>
<html><body><h1>Baseline Ticket UI - Mock</h1><p>Preview artifact for baseline.</p></body></html>
HTML

echo "Baseline tests and evaluation completed. Results written to results/"
