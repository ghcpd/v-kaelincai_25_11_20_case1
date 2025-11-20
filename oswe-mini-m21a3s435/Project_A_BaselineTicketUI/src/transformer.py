"""
Baseline transformer simulating the original Ticket UI behavior.
It performs minimal transformation and doesn't implement hierarchy improvements.
"""
from typing import Any, Dict


def transform_layout(layout: Dict[str, Any]) -> Dict[str, Any]:
    """Return a minimal transformed structure that preserves original order and types.
    Designed to represent the baseline (unimproved) UI.
    """
    # Defensive copy
    import copy
    result = copy.deepcopy(layout)

    # Baseline: mark as transformed with no changes. Collect warnings.
    result.setdefault('_meta', {})
    result['_meta']['transformed_by'] = 'baseline'
    result['_meta']['warnings'] = []

    # detect unsafe html entries
    def walk(obj, path="root"):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k.lower() in ('html','unsafe_html') and isinstance(v, str) and '<script' in v.lower():
                    result['_meta']['warnings'].append(f"Unsafe HTML at {path}.{k}")
                walk(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                walk(item, f"{path}[{i}]")

    walk(result)
    return result


# Minimal metrics used by test harness

def compute_hierarchy_score(transformed: Dict[str, Any]) -> float:
    """Baseline uses a naive heuristic: find position of 'core' or 'problem_description'. Lower is worse.
    Returns score between 0 and 1, higher is better clarity.
    """
    # very naive: core at top => score 1.0, else 0.2
    keys = []
    root = transformed.get('layout', transformed)
    if isinstance(root, dict):
        keys = list(root.keys())
    core_found = any('problem' in k.lower() or 'core' in k.lower() for k in keys)
    return 1.0 if core_found and list(keys).index(next(k for k in keys if 'problem' in k.lower() or 'core' in k.lower()))==0 else 0.2
