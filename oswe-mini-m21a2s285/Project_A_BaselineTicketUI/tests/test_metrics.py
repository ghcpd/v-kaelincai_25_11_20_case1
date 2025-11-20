import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))
from transform import baseline_transform


def test_baseline_no_restructuring():
    layout = {'core': {'description':'x','priority':'Low'}, 'history': {'entries': ['a','b','c']}, 'attachments': {'list':[{'name':'f'}]}}
    out = baseline_transform(layout)
    assert out['metrics']['core_on_top'] is False


def test_sanitization_baseline():
    layout = {'core': {'description':'<script>bad</script>'}}
    out = baseline_transform(layout)
    assert '&lt;' in out['layout']['core']['description'] or 'missing_description' in out['ui_warnings']

if __name__ == '__main__':
    test_baseline_no_restructuring()
    test_sanitization_baseline()
    print('Baseline metric tests ran')
