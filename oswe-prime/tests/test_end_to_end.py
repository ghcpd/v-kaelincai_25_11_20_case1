import json
import os
import sys
from pathlib import Path

# Allow importing project harnesses
sys.path.append(str(Path(__file__).absolute().parents[1] / 'Project_A_BaselineTicketUI' / 'src'))
sys.path.append(str(Path(__file__).absolute().parents[1] / 'Project_B_EnhancedTicketUI' / 'src'))

import importlib.util

# Helper to load harness and its local transformer module in isolation
def load_harness(project_dir, harness_name):
    # paths to transformer and harness
    transformer_path = Path(project_dir) / 'src' / 'transformer.py'
    harness_path = Path(project_dir) / 'src' / 'harness.py'

    # load transformer with unique name
    t_spec = importlib.util.spec_from_file_location(f"{harness_name}_transformer", str(transformer_path))
    t_mod = importlib.util.module_from_spec(t_spec)
    t_spec.loader.exec_module(t_mod)

    # store original 'transformer' mapping and set ours
    orig_transformer = sys.modules.get('transformer')
    sys.modules['transformer'] = t_mod
    try:
        # load harness using unique name
        h_spec = importlib.util.spec_from_file_location(harness_name, str(harness_path))
        h_mod = importlib.util.module_from_spec(h_spec)
        h_spec.loader.exec_module(h_mod)
    finally:
        # restore original transformer mapping
        if orig_transformer is not None:
            sys.modules['transformer'] = orig_transformer
        else:
            sys.modules.pop('transformer', None)
    return h_mod

# Load baseline harness
baseline_project = Path(__file__).absolute().parents[1] / 'Project_A_BaselineTicketUI'
enhanced_project = Path(__file__).absolute().parents[1] / 'Project_B_EnhancedTicketUI'
baseline_h = load_harness(baseline_project, 'baseline_harness')
run_baseline = baseline_h.run_scenarios

# Load enhanced harness
enh_h = load_harness(enhanced_project, 'enhanced_harness')
run_enhanced = enh_h.run_scenarios


def load_scenarios():
    scenario_path = Path(os.getenv('SCENARIO_PATH', Path(__file__).absolute().parents[1] / 'shared' / 'test_scenarios.json'))
    with open(scenario_path, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def test_end_to_end_and_compare():
    s = load_scenarios()
    pre_results = run_baseline(s)
    post_results = run_enhanced(s)

    # Save JSON outputs
    outdir = Path('results')
    outdir.mkdir(exist_ok=True)
    with open(outdir / 'results_pre.json', 'w') as fh:
        json.dump(pre_results, fh, indent=2)
    with open(outdir / 'results_post.json', 'w') as fh:
        json.dump(post_results, fh, indent=2)

    # Validate the clarifying improvements: for each scenario where expected core_on_top, ensure post > pre
    for pr, po, scen in zip(pre_results, post_results, s):
        exp = scen.get('expected', {})
        if exp.get('core_on_top'):
            assert po['metrics']['hierarchy_clarity_score'] >= pr['metrics']['hierarchy_clarity_score']
        if exp.get('timeline_collapsed'):
            # enhanced should have collapsed sections > baseline
            assert po['metrics'].get('collapsed_sections_count', 0) >= pr['metrics'].get('collapsed_sections_count', 0)
        if exp.get('preview_blocking') is False:
            # attachments preview mode should exist in enhanced
            found_post = any(((f.get('type') == 'attachments') or (f.get('label') == 'attachments')) and f.get('ui', {}).get('preview_mode') == 'side-panel' for f in po['output_layout']['fields'])
            assert found_post
        if exp.get('internal_clear'):
            found_post = any(f.get('type') == 'notes' and f.get('ui', {}).get('internal') for f in po['output_layout']['fields'])
            assert found_post
        if exp.get('safe_fallback'):
            # enhanced should detect unsafe HTML or invalid fields
            assert 'unsafe_html_detected' in po['ui_warnings'] or len(po['errors']) > 0

    # Basic improvements metric
    avg_pre = sum(r['metrics']['hierarchy_clarity_score'] for r in pre_results) / len(pre_results)
    avg_post = sum(r['metrics']['hierarchy_clarity_score'] for r in post_results) / len(post_results)
    assert avg_post >= avg_pre
