import json
import sys
from pathlib import Path


def load_results(path):
    try:
        with open(path) as fh:
            return json.load(fh)
    except Exception:
        return []


def compute_summary(results):
    total = len(results)
    passed = sum(1 for r in results if r.get('pass'))
    avg_hierarchy = 0
    avg_misop = 0
    if total > 0:
        avg_hierarchy = sum(r.get('metrics', {}).get('hierarchy_clarity_score', 0) for r in results) / total
        avg_misop = sum(r.get('metrics', {}).get('mis_operation_risk', 0) for r in results) / total
    return {'total': total, 'passed': passed, 'avg_hierarchy': avg_hierarchy, 'avg_misop': avg_misop}


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: compare_results.py pre.json post.json out.md')
        sys.exit(2)
    pre = load_results(sys.argv[1])
    post = load_results(sys.argv[2])
    out = Path(sys.argv[3])

    pre_s = compute_summary(pre)
    post_s = compute_summary(post)

    lines = []
    lines.append('# Compare Report\n')
    lines.append('## Summary\n')
    lines.append(f'- Scenarios: {pre_s["total"]} vs {post_s["total"]}\n')
    lines.append(f'- Passed: {pre_s["passed"]} vs {post_s["passed"]}\n')
    lines.append('\n')
    lines.append('## Hierarchy Clarity\n')
    lines.append(f'- Baseline avg hierarchy score: {pre_s["avg_hierarchy"]:.2f}\n')
    lines.append(f'- Enhanced avg hierarchy score: {post_s["avg_hierarchy"]:.2f}\n')
    lines.append(f'- Delta: {post_s["avg_hierarchy"] - pre_s["avg_hierarchy"]:.2f}\n')
    lines.append('\n')
    lines.append('## Mis-operation Risk\n')
    lines.append(f'- Baseline avg mis-operation risk: {pre_s["avg_misop"]:.2f}\n')
    lines.append(f'- Enhanced avg mis-operation risk: {post_s["avg_misop"]:.2f}\n')
    lines.append(f'- Delta: {pre_s["avg_misop"] - post_s["avg_misop"]:.2f}\n')
    lines.append('\n')
    # Edge-case coverage and collapsibility/preview metrics
    pre_edge = sum(1 for r in pre if len(r.get('ui_warnings', [])) > 0 or len(r.get('errors', [])) > 0)
    post_edge = sum(1 for r in post if len(r.get('ui_warnings', [])) > 0 or len(r.get('errors', [])) > 0)
    lines.append('## Edge-case handling\n')
    lines.append(f'- Baseline edge-case flagged scenarios: {pre_edge}/{pre_s["total"]}\n')
    lines.append(f'- Enhanced edge-case flagged scenarios: {post_edge}/{post_s["total"]}\n')

    lines.append('\n')
    lines.append('## Collapsibility / Attachment preview differences\n')
    for pr, po in zip(pre, post):
        collapses_pre = sum(1 for f in pr.get('output_layout', {}).get('fields', []) if f.get('ui', {}).get('collapsed'))
        collapses_post = sum(1 for f in po.get('output_layout', {}).get('fields', []) if f.get('ui', {}).get('collapsed'))
        attachments_pre = any(((f.get('type') == 'attachments') or (f.get('label') == 'attachments')) and f.get('ui', {}).get('preview_mode') for f in pr.get('output_layout', {}).get('fields', []))
        attachments_post = any(((f.get('type') == 'attachments') or (f.get('label') == 'attachments')) and f.get('ui', {}).get('preview_mode') for f in po.get('output_layout', {}).get('fields', []))
        lines.append(f'### {pr.get("id")} collapses: pre {collapses_pre} vs post {collapses_post} | attachments_pre: {attachments_pre} vs attachments_post: {attachments_post}\n')

    # differences per scenario
    lines.append('\n')
    lines.append('## Scenario-by-scenario results\n')
    for pr, po in zip(pre, post):
        lines.append(f'### {pr.get("id")}\n')
        lines.append(f'- Baseline pass: {pr.get("pass")} | Enhanced pass: {po.get("pass")}\n')
        lines.append(f'- Baseline hierarchy: {pr.get("metrics", {}).get("hierarchy_clarity_score")} | Enhanced: {po.get("metrics", {}).get("hierarchy_clarity_score")}\n')
        lines.append(f'- Baseline misop: {pr.get("metrics", {}).get("mis_operation_risk")} | Enhanced: {po.get("metrics", {}).get("mis_operation_risk")}\n')
        lines.append('\n')
    lines.append('## Improvement analysis\n')
    lines.append(f'- Average hierarchy clarity delta: {post_s["avg_hierarchy"] - pre_s["avg_hierarchy"]:.2f}\n')
    lines.append(f'- Average mis-operation risk reduction: {pre_s["avg_misop"] - post_s["avg_misop"]:.2f}\n')
    lines.append(f'- Edge-case coverage improved by: {pre_edge - post_edge}\n')

    out.write_text('\n'.join(lines))
    print('Compare report written to', out)
