import json
import os
from src.transformer import transform_layout, compute_hierarchy_score

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCENARIO_FILE = os.path.join(ROOT, '..', 'test_scenarios.json')


def load_scenarios():
    with open(SCENARIO_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_baseline_runs_and_scores():
    scenarios = load_scenarios()
    assert isinstance(scenarios, list) and len(scenarios) >= 5

    for s in scenarios:
        out = transform_layout(s['input'])
        assert out.get('_meta', {}).get('transformed_by') == 'baseline'
        score = compute_hierarchy_score(out)
        assert 0.0 <= score <= 1.0
