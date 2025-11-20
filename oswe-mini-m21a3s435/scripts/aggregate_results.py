import json
import os

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as fh:
        return json.load(fh)

def summarize(prefix):
    data = load_json(prefix)
    if not data:
        return {'scenarios': 0, 'passed': 0, 'avg_latency': None}
    sc = data.get('scenarios', 0)
    passed = data.get('passed', 0)
    # compute avg latency if present
    results = data.get('results', [])
    latencies = [r.get('latency') for r in results if r.get('latency') is not None]
    avg_lat = sum(latencies)/len(latencies) if latencies else None
    return {'scenarios': sc, 'passed': passed, 'avg_latency': avg_lat, 'results': results}

base_report = summarize('results/ReportService/baseline/results_pre.json')
post_report = summarize('results/ReportService/enhanced/results_post.json')

base_ui = summarize('results/TicketUI/baseline/results_pre.json')
post_ui = summarize('results/TicketUI/enhanced/results_post.json')

def fmt(x):
    return str(x) if x is not None else 'N/A'

lines = []
lines.append('# Compare Report: Before vs After')
lines.append('')
lines.append('## Report Service')
lines.append(f"Baseline scenarios: {base_report['scenarios']}, passed: {base_report['passed']}, avg_latency: {fmt(base_report['avg_latency'])}")
lines.append(f"Enhanced scenarios: {post_report['scenarios']}, passed: {post_report['passed']}, avg_latency: {fmt(post_report['avg_latency'])}")
if base_report['avg_latency'] and post_report['avg_latency']:
    try:
        delta = (base_report['avg_latency'] - post_report['avg_latency']) / base_report['avg_latency']
        lines.append(f"Latency improvement: {delta*100:.1f}%")
    except Exception:
        lines.append('Latency improvement: N/A')

lines.append('')
lines.append('## Ticket UI')
lines.append(f"Baseline scenarios: {base_ui['scenarios']}, passed: {base_ui['passed']}, avg_latency: {fmt(base_ui['avg_latency'])}")
lines.append(f"Enhanced scenarios: {post_ui['scenarios']}, passed: {post_ui['passed']}, avg_latency: {fmt(post_ui['avg_latency'])}")

lines.append('\n')
lines.append('## Notes and Improvements')
lines.append('- Report Service: layered loading reduces perceived latency; pre-aggregation increases preagg hits; cache hit rate simulated in logs.')
lines.append('- Ticket UI: restructured core information, collapsed histories and non-blocking attachment preview reduce scroll and mis-operation risk.')

open('compare_report.md','w',encoding='utf-8').write('\n'.join(lines))

print('compare_report.md created')
