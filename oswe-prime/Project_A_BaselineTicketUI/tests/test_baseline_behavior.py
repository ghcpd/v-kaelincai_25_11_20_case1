import json
import os
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).absolute().parents[1] / 'src'))
from harness import run_scenarios


def test_baseline_behaviors_do_not_apply_enhancements():
    scenario_path = Path(os.getenv('SCENARIO_PATH', Path(__file__).absolute().parents[2] / 'shared' / 'test_scenarios.json'))
    with open(scenario_path, 'r', encoding='utf-8') as fh:
        scenarios = json.load(fh)
    results = run_scenarios(scenarios)
    # Baseline should not require confirmation for ambiguous actions
    for r in results:
        if r['id'] == 'mis_operation_flow':
            # action fields present
            action_fields = [f for f in r['output_layout']['fields'] if f.get('type') == 'action']
            for a in action_fields:
                # baseline does not attach require_confirmation
                assert not a.get('ui', {}).get('require_confirmation')
            if r['id'] == 'long_scroll_flow':
                # baseline should not collapse history
                assert r['metrics'].get('collapsed_sections_count', 0) == 0

