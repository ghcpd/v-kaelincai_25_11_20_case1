import json
import os
from pathlib import Path

from transform import enhance_transform

ROOT = Path(__file__).resolve().parents[2]
SCENARIO_FILE = ROOT / 'test_scenarios.json'
RESULTS_DIR = ROOT / 'results'
RESULTS_DIR.mkdir(exist_ok=True)


def run_all():
    with SCENARIO_FILE.open('r', encoding='utf-8') as f:
        scenarios = json.load(f)

    results = []
    for s in scenarios:
        rid = s['id']
        out = enhance_transform(s.get('input'))
        results.append({'id': rid, 'enhanced': out})

    with (RESULTS_DIR / 'results_post.json').open('w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    with (RESULTS_DIR / 'log_post.txt').open('w', encoding='utf-8') as f:
        f.write('Enhanced run completed\n')

    # also generate a simple visual prototype (HTML)
    html = '<html><body><h1>Prototype</h1><p>This is a lightweight visual artifact for tests.</p></body></html>'
    with (RESULTS_DIR / 'prototype.html').open('w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    run_all()
    print('Enhanced scenario run complete')
