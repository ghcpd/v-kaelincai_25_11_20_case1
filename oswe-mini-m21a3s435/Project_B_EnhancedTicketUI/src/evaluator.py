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
        expected = s.get('expected', {})
        try:
            out = transform_layout(inp)
            metrics = out.get('metrics', {})
            warnings = out.get('warnings', [])
            errors = out.get('errors', [])
            # simple validations against expected where provided
            ok = True
            if 'metrics' in expected:
                for k,v in expected['metrics'].items():
                    if k in metrics:
                        # allow approximate numeric matching
                        if isinstance(v, (int,float)):
                            if abs(metrics.get(k,0)-v) > 0.5 and v<=1.0:
                                ok = False
                        else:
                            if metrics.get(k) != v:
                                ok = False

            status = 'ok' if ok else 'mismatch'
        except Exception as e:
            out = {'error': str(e)}
            metrics = {}
            warnings = []
            errors = [str(e)]
            status = 'error'

        res = {
            'name': name,
            'status': status,
            'metrics': metrics,
            'warnings': warnings,
            'errors': errors
        }
        results.append(res)
        logs.append(f"{name}: status={status} metrics={metrics}")

    # write outputs
    open(os.path.join(out_dir, 'results_post.json'), 'w', encoding='utf-8').write(json.dumps({'results': results}, indent=2))
    open(os.path.join(out_dir, 'log_post.txt'), 'w', encoding='utf-8').write('\n'.join(logs))

    # compute coverage
    summary = {
        'total': len(results),
        'passed': sum(1 for r in results if r['status']=='ok'),
        'avg_hierarchy': sum(r['metrics'].get('hierarchy_clarity',0) for r in results)/max(1,len(results))
    }
    open(os.path.join(out_dir, 'summary_post.json'), 'w', encoding='utf-8').write(json.dumps(summary, indent=2))


if __name__ == '__main__':
    ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    SCEN = os.path.join(ROOT, '..', 'test_scenarios.json')
    OUT = os.path.join(ROOT, '..', 'results')
    evaluate_all(SCEN, OUT)
