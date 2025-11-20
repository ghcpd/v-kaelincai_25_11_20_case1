import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
pre_path = ROOT / 'results' / 'results_pre.json'
post_path = ROOT / 'results' / 'results_post.json'
report = ROOT / 'compare_report.md'

# Basic defaults
pre = []
post = []

if pre_path.exists():
    pre = json.loads(pre_path.read_text(encoding='utf-8'))
if post_path.exists():
    post = json.loads(post_path.read_text(encoding='utf-8'))

# Build quick metrics
scenarios = set([r.get('id') for r in pre] + [r.get('id') for r in post])
rows = []
improvement_count = 0

for s in scenarios:
    a = next((x for x in pre if x.get('id')==s), {})
    b = next((x for x in post if x.get('id')==s), {})
    # baseline metrics
    base_core_top = False
    if a:
        m = a.get('baseline', {}).get('metrics', {})
        base_core_top = m.get('core_on_top', False)
    # enhanced metrics
    enh_core_top = False
    if b:
        m = b.get('enhanced', {}).get('metrics', {})
        enh_core_top = m.get('core_on_top', False)
    improved = (not base_core_top) and enh_core_top
    rows.append({'id': s, 'base_core_top': base_core_top, 'enh_core_top': enh_core_top, 'improved': improved})
    if improved:
        improvement_count += 1

with report.open('w', encoding='utf-8') as f:
    f.write('# Hierarchy & Behavior Comparison Report\n\n')
    f.write('Scenarios tested: {}\n\n'.format(len(scenarios)))
    f.write('## Summary\n')
    f.write('- Baseline core on top: {}\n'.format(sum(1 for r in rows if r['base_core_top'])))
    f.write('- Enhanced core on top: {}\n'.format(sum(1 for r in rows if r['enh_core_top'])))
    f.write('- Improvements: {}\n\n'.format(improvement_count))

    f.write('## Scenario Details\n')
    for r in rows:
        f.write('- {}: base_core_top={}, enh_core_top={}, improved={}\n'.format(r['id'], r['base_core_top'], r['enh_core_top'], r['improved']))

print('Comparison report generated at', report)
