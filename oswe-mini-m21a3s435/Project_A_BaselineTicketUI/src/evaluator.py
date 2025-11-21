import json
import os
from src.transformer import transform_layout, compute_hierarchy_score


def evaluate_all(scenarios_path: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    with open(scenarios_path, 'r', encoding='utf-8') as f:
        scenarios = json.load(f)

    results = []
    logs = []
    for s in scenarios:
        name = s.get('name', '<unnamed>')
        inp = s.get('input')
        try:
            out = transform_layout(inp)
            score = compute_hierarchy_score(out)
            passed = True
            status = 'ok'
        except Exception as e:
            out = {'error': str(e)}
            score = 0.0
            passed = False
            status = 'error'

        res = {
            'name': name,
            'status': status,
            'hierarchy_score': score,
            'warnings': out.get('_meta', {}).get('warnings', []) if isinstance(out, dict) else []
        }
        results.append(res)
        logs.append(f"{name}: status={status}, score={score}")

    # write outputs
    open(os.path.join(out_dir, 'results_pre.json'), 'w', encoding='utf-8').write(json.dumps({'results': results}, indent=2))
    open(os.path.join(out_dir, 'log_pre.txt'), 'w', encoding='utf-8').write('\n'.join(logs))

    # simple summary
    summary = {
        'total': len(results),
        'passed': sum(1 for r in results if r['status']=='ok'),
        'avg_hierarchy': sum(r['hierarchy_score'] for r in results) / max(1, len(results))
    }
    open(os.path.join(out_dir, 'summary_pre.json'), 'w', encoding='utf-8').write(json.dumps(summary, indent=2))


if __name__ == '__main__':
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    SCEN = os.path.join(ROOT, '..', 'test_scenarios.json')
    OUT = os.path.join(ROOT, '..', 'results')
    evaluate_all(SCEN, OUT)
