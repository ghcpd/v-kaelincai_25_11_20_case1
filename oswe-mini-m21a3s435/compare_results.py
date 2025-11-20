import json
import os

def load_json(p):
    if not os.path.exists(p):
        return {}
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    base_a = 'Project_A_BaselineTicketUI/results/results_pre.json'
    base_b = 'Project_B_EnhancedTicketUI/results/results_post.json'
    a = load_json(base_a).get('results', [])
    b = load_json(base_b).get('results', [])

    total = max(len(a), len(b))
    passed_a = sum(1 for r in a if r.get('status')=='ok')
    passed_b = sum(1 for r in b if r.get('status')=='ok')

    # hierarchy clarity averages
    avg_a = sum((r.get('hierarchy_score') if 'hierarchy_score' in r else r.get('metrics',{}).get('hierarchy_clarity',0)) for r in a)/max(1,len(a)) if a else 0
    avg_b = sum((r.get('metrics',{}).get('hierarchy_clarity',0)) for r in b)/max(1,len(b)) if b else 0

    # Collapsibility comparison
    collapsed_a = sum(r.get('metrics',{}).get('collapsed_sections',0) for r in a)
    collapsed_b = sum(r.get('metrics',{}).get('collapsed_sections',0) for r in b)

    mis_a = sum(r.get('metrics',{}).get('misoperation_risk',0) for r in a)
    mis_b = sum(r.get('metrics',{}).get('misoperation_risk',0) for r in b)

    report = []
    report.append('# Compare Report: Baseline vs Enhanced')
    report.append('')
    report.append(f'- Total scenarios: {total}')
    report.append(f'- Passed (baseline): {passed_a}/{len(a)}')
    report.append(f'- Passed (enhanced): {passed_b}/{len(b)}')
    report.append('')
    report.append('## Hierarchy clarity (avg)')
    report.append(f'- Baseline: {avg_a:.3f}')
    report.append(f'- Enhanced: {avg_b:.3f}')
    report.append(f'- Delta (improvement): {avg_b - avg_a:.3f}')
    report.append('')
    report.append('## Collapsibility')
    report.append(f'- Baseline collapsed sections (sum): {collapsed_a}')
    report.append(f'- Enhanced collapsed sections (sum): {collapsed_b}')
    report.append('')
    report.append('## Mis-operation risk (lower better)')
    report.append(f'- Baseline total risk score: {mis_a:.3f}')
    report.append(f'- Enhanced total risk score: {mis_b:.3f}')
    report.append('')
    report.append('## Per-scenario comparison')
    for i in range(total):
        a_row = a[i] if i < len(a) else {}
        b_row = b[i] if i < len(b) else {}
        name = a_row.get('name') or b_row.get('name') or f'scenario_{i}'
        report.append(f'### {name}')
        report.append(f'- baseline: {a_row.get("status")} metrics={a_row.get("metrics") or a_row.get("hierarchy_score")}')
        report.append(f'- enhanced: {b_row.get("status")} metrics={b_row.get("metrics")}')
        report.append('')

    # output
    os.makedirs('results', exist_ok=True)
    with open('compare_report.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))


if __name__ == '__main__':
    main()
