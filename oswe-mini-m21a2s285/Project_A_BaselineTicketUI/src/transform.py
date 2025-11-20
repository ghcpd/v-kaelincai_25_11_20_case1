"""
Baseline transformation - minimal processing: returns input structure with light validation and computed metrics.
Does not reorder or improve UI. Simulated UI model for Ticket Detail Page.
"""
import json
import copy

SAFE_TAGS = ['b','i','u','em','strong','p','br']


def sanitize_html(text):
    if not isinstance(text, str):
        return text
    # naive sanitize: remove <> pairs to avoid unsafe payloads
    return text.replace('<', '&lt;').replace('>', '&gt;')


def baseline_transform(layout):
    """Return a shallow transform: ensure required fields and compute metrics."""
    out = copy.deepcopy(layout)
    metrics = {}
    warnings = []

    # Ensure core fields exist
    core = out.get('core', {})
    if 'description' not in core:
        warnings.append('missing_description')
        core.setdefault('description', 'No description provided')
    core.setdefault('priority', 'Normal')
    core.setdefault('status', 'Open')
    out['core'] = core

    # sanitize content
    for section, content in out.items():
        if isinstance(content, dict):
            for k, v in content.items():
                if isinstance(v, str):
                    out[section][k] = sanitize_html(v)

    # compute naive metrics
    total_fields = sum(len(v) if isinstance(v, dict) else 1 for v in out.values())
    metrics['total_fields'] = total_fields
    metrics['core_on_top'] = False  # baseline doesn't move core

    status = 'ok' if not warnings else 'warning'
    return {'layout': out, 'metrics': metrics, 'ui_warnings': warnings, 'status': status}


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(json.dumps(baseline_transform(data), indent=2))
