#!/usr/bin/env bash
set -e
ROOT_DIR=$(pwd)
echo "Running Project B enhanced tests..."
python -m pytest -q

mkdir -p results
python -u -c "from src.evaluator import evaluate_all;import os;print('Evaluating scenarios...');evaluate_all(os.path.abspath('../test_scenarios.json'), os.path.abspath('results'))"

# generate simple mock HTML artifact showing improved layout
cat > results/enhanced_preview.html <<'HTML'
<!doctype html>
<html><body><h1>Enhanced Ticket UI - Mock</h1><p>Sections should be reordered: core info at the top, history collapsed, attachments side-panel.</p></body></html>
HTML

echo "Enhanced tests and evaluation completed. Results written to results/"
