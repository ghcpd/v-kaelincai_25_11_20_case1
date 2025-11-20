import json
import os
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).absolute().parents[1] / 'src'))
from harness import run_scenarios


def test_core_fields_top_and_attachment_preview_and_confirmation():
    scenario_path = Path(os.getenv('SCENARIO_PATH', Path(__file__).absolute().parents[2] / 'shared' / 'test_scenarios.json'))
    with open(scenario_path, 'r', encoding='utf-8') as fh:
        scenarios = json.load(fh)
    results = run_scenarios(scenarios)
    # Find normal_flow and mis_operation_flow
    for r in results:
        if r['id'] == 'normal_flow':
            # core fields should be at top (hierarchy score >= 66)
            assert r['metrics']['hierarchy_clarity_score'] >= 66
            # attachments preview shouldn't be blocking
            attachments = [f for f in r['output_layout']['fields'] if f.get('type') == 'attachments' or f.get('label') == 'attachments']
            for a in attachments:
                assert a.get('ui', {}).get('preview_mode') == 'side-panel'
        if r['id'] == 'mis_operation_flow':
            # ambiguous actions must require confirmation
            action_fields = [f for f in r['output_layout']['fields'] if f.get('type') == 'action']
            for a in action_fields:
                assert a.get('ui', {}).get('require_confirmation') is True
        if r['id'] == 'malformed_input':
            # Enhanced should detect unsafe content and invalid field types
            assert 'unsafe_html_detected' in r['ui_warnings'] or 'unsafe_html_detected' in r['errors']
            assert 'invalid_field_type' in r['errors']
        if r['id'] == 'complex_nesting':
            # status should be present and core fields preserved
            labels = [f.get('label') for f in r['output_layout']['fields']]
            assert 'status' in labels
        if r['id'] == 'long_scroll_flow':
            assert r['metrics'].get('collapsed_sections_count', 0) > 0

