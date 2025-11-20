import json
import os
from pathlib import Path
import sys

# allow import from src
sys.path.append(str(Path(__file__).absolute().parents[1] / 'src'))

from harness import run_scenarios


def test_baseline_runs_and_writes_results():
    # find test scenarios
    scaffold_root = Path(__file__).absolute().parents[2]
    scenario_path = Path(os.getenv('SCENARIO_PATH', scaffold_root / 'shared' / 'test_scenarios.json'))
    with open(scenario_path, 'r', encoding='utf-8') as fh:
        scenarios = json.load(fh)

    results = run_scenarios(scenarios)
    assert isinstance(results, list)
    # Some minimal assertion to ensure baseline outputs metrics
    for r in results:
        assert 'metrics' in r
        assert isinstance(r['metrics'], dict)
