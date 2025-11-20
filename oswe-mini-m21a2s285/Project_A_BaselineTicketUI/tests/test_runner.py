import json
import os
from pathlib import Path

from transform import baseline_transform

ROOT = Path(__file__).resolve().parents[2]
SCENARIO_FILE = ROOT / 'test_scenarios.json'
RESULTS_DIR = ROOT / 'results'
RESULTS_DIR.mkdir(exist_ok=True)


def run_all():
    with SCENARIO_FILE.open('r', encoding='utf-8') as f:
        scenarios = json.load(f)

    results = []
    for s in scenarios:
        res = {'id': s['id'], 'baseline': None}
        out = baseline_transform(s.get('input'))
        # baseline expectations: no core_on_top, no non_blocking attachment
        metrics = out.get('metrics', {})
        res['baseline'] = out
        results.append(res)

    with (RESULTS_DIR / 'results_pre.json').open('w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    with (RESULTS_DIR / 'log_pre.txt').open('w', encoding='utf-8') as f:
        f.write('Baseline run completed\n')
    # generate a small prototype artifact
    html = '<html><body><h2>Baseline Prototype</h2><p>Baseline UI - simple.</p></body></html>'
    with (RESULTS_DIR / 'prototype.html').open('w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    run_all()
    print('Baseline scenario run complete')
