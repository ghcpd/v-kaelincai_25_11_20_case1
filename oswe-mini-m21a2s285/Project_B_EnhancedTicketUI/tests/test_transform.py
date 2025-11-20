import json
import os
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))
from transform import enhance_transform


def run_tests():
    cases = []
    cases.append({
        'core': {'description': '<script>alert(1)</script>Broken view', 'priority': 'High', 'status': 'Open'},
        'history': {'entries': ['h1','h2','h3','h4']},
        'attachments': {'list': [{'name':'file.txt'}]}
    })
    cases.append({'core': 'improper core', 'notes': {'items': [{'internal': True, 'text': 'admin note'}]}})
    cases.append(['not a dict'])
    for c in cases:
        out = enhance_transform(c)
        assert out['metrics']['core_on_top'] is True
        assert 'clarity_score' in out['metrics']
    print('Enhanced tests passed')

if __name__ == '__main__':
    run_tests()
    print('Enhanced tests OK')
