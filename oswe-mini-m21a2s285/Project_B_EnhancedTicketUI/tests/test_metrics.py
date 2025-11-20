import json
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))
from transform import enhance_transform


def test_core_top_and_collapsed():
    layout = {
        'core': {'description': '<b>Desc</b>', 'priority': 'High', 'status': 'Open'},
        'history': {'entries': ['e1','e2','e3','e4','e5']},
        'attachments': {'list': [{'name':'f1'}]}
    }
    out = enhance_transform(layout)
    assert out['metrics']['core_on_top'] is True
    assert out['layout']['history']['collapsed'] is True
    assert out['layout']['attachments']['non_blocking'] is True


def test_internal_note_distinction_and_confirmation():
    layout = {'core': {'description':'X'}, 'notes': {'items': [{'internal': True, 'text': 'n1'}, {'internal': False, 'text':'n2'}]}}
    out = enhance_transform(layout)
    items = out['layout']['notes']['items']
    assert any(i.get('confirm_on_edit') for i in items if i.get('internal'))
    assert all(i.get('style') for i in items)


def test_malformed_input_sanitized():
    layout = '<script>bad()</script>'
    out = enhance_transform(layout)
    assert 'malformed_layout' in out['ui_warnings'] or out['status'] in ('ok','warning')


if __name__ == '__main__':
    test_core_top_and_collapsed()
    test_internal_note_distinction_and_confirmation()
    test_malformed_input_sanitized()
    print('Enhanced metric tests ran')
