import json
import os
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parents[1] / 'src'))
from transform import baseline_transform


def run_simple_case():
    layout = {
        'core': {'description': 'Something broke', 'priority': 'High', 'status': 'Open'},
        'history': {'entries': ['a', 'b']},
        'attachments': {'list': [{'name': 'log.txt'}]}
    }
    out = baseline_transform(layout)
    assert out['metrics']['core_on_top'] is False
    assert 'missing_description' not in out['ui_warnings']
    print('baseline simple case passed')


if __name__ == '__main__':
    run_simple_case()
    print('Baseline tests OK')
