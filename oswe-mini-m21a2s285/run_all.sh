#!/usr/bin/env bash
set -e
# Run baseline
(cd Project_A_BaselineTicketUI; bash run_tests.sh)
# Run enhanced
(cd Project_B_EnhancedTicketUI; bash run_tests.sh)
# Aggregate
mkdir -p results
cp Project_A_BaselineTicketUI/results/results_pre.json results/results_pre.json || true
cp Project_B_EnhancedTicketUI/results/results_post.json results/results_post.json || true
# Use comparison tool for richer report
python tools/compare_runs.py || (
  echo 'compare_runs.py failed — fallback to simple report';
  python - <<'PY'
import json,sys
pre='results/results_pre.json'
post='results/results_post.json'
try:
    a=json.load(open(pre))
    b=json.load(open(post))
except Exception as e:
    print('Failed to load results',e); sys.exit(1)
report='compare_report.md'
with open(report,'w') as f:
    f.write('# Comparison Report\n')
    f.write('- Total scenarios pre: {}\n'.format(len(a)))
    f.write('- Total scenarios post: {}\n'.format(len(b)))
    f.write('\n')
    f.write('## Differences (sketch)\n')
    f.write('- Enhanced places core on top, baseline does not.\n')
    f.write('- Collapsible sections implemented in enhanced.\n')
    f.write('- Attachment preview changed to side-panel.\n')
print('Aggregated results and report written')
PY
)
