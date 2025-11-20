import json
import os
from src.transformer import transform_layout, compute_hierarchy_score

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCENARIO_FILE = os.path.join(ROOT, '..', 'test_scenarios.json')


def load_scenarios():
    with open(SCENARIO_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_enhanced_transform_moves_core_top():
    scenarios = load_scenarios()
    # check overloaded_standard scenario
    scenario = next(s for s in scenarios if s['name']=='overloaded_standard')
    out = transform_layout(scenario['input'])
    assert out.get('metrics', {}).get('hierarchy_clarity', 0) >= 0.8


def test_collapsed_sections_and_attachments():
    scenarios = load_scenarios()
    s = next(s for s in scenarios if s['name']=='long_history_scroll')
    out = transform_layout(s['input'])
    # timeline should be collapsed and have preview
    sections = out.get('ui', {}).get('sections', [])
    timeline = next((sec for sec in sections if 'timeline' in (sec.get('name','').lower())), None)
    assert timeline is not None and timeline.get('collapsed')
    assert ('_preview' in timeline) or (len(timeline.get('items',[]))<=5)


def test_attachment_preview_non_blocking_and_side_panel():
    scenarios = load_scenarios()
    s = next(s for s in scenarios if s['name']=='overloaded_standard')
    out = transform_layout(s['input'])
    sections = out.get('ui', {}).get('sections', [])
    att = next((sec for sec in sections if sec.get('type')=='attachment' or 'attachment' in sec.get('name','').lower()), None)
    assert att is not None
    assert att.get('_attachment_mode') == 'side-panel' and att.get('_preview_inline') is True


def test_misoperation_prevention_and_confirmation():
    scenarios = load_scenarios()
    s = next(s for s in scenarios if s['name']=='misoperation_confusion')
    out = transform_layout(s['input'])
    # actions should be flagged for confirmation
    sections = out.get('ui', {}).get('sections', [])
    controls = next((sec for sec in sections if sec.get('type')=='actions' or 'control' in sec.get('name','').lower()), None)
    assert controls is not None
    actions = controls.get('items', [])
    assert any(a.get('requires_confirmation') or a.get('critical') for a in actions)


def test_notes_differentiated_internal_vs_customer():
    scenarios = load_scenarios()
    s = next(s for s in scenarios if s['name']=='misoperation_confusion')
    out = transform_layout(s['input'])
    secs = out.get('ui', {}).get('sections', [])
    note = next((sec for sec in secs if sec.get('type')=='note' or 'note' in sec.get('name','').lower()), None)
    assert note is not None
    # should have both internal and customer types present in items or classification
    assert any(n.get('_display')=='internal' or n.get('visibility')=='internal' for n in note.get('items', []) ) or note.get('_display') in ('internal','customer')


def test_malformed_and_unsafe_html():
    scenarios = load_scenarios()
    s = next(s for s in scenarios if s['name']=='malformed_unsafe_html')
    out = transform_layout(s['input'])
    # check that warnings were raised for removed script tags
    assert any('script removed' in w for w in out.get('warnings', [])) or any('script removed' in w for w in out.get('errors', []))


def test_complex_nesting_safe_degrade():
    scenarios = load_scenarios()
    s = next(s for s in scenarios if s['name']=='complex_nesting')
    out = transform_layout(s['input'])
    # complex nesting should produce errors and mark items safely
    assert isinstance(out.get('errors', []), list)
    # check that attachments items are normalized (no raw ints)
    secs = out.get('ui', {}).get('sections', [])
    att = next((sec for sec in secs if 'attachment' in sec.get('name','').lower()), None)
    if att:
        for it in att.get('items', []):
            assert isinstance(it, dict)
