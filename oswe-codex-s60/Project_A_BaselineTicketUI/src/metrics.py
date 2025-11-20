from typing import Any, Dict
try:
    from .utils import traverse_nodes, find_first
except ImportError:  # pragma: no cover
    from utils import traverse_nodes, find_first

CORE_IDS = {"description", "priority", "status"}


def compute_hierarchy_clarity(layout: Dict[str, Any]) -> float:
    """Naive clarity: reward presence, shallow depth, and early order of core info."""
    if not isinstance(layout, dict):
        return 0.0
    score = 0.0
    depth_penalty = 0.1
    order_penalty = 0.08

    # Map id -> position among top-level children if exists
    top_positions = {}
    if isinstance(layout.get("children"), list):
        for idx, child in enumerate(layout["children"]):
            if isinstance(child, dict) and "id" in child:
                top_positions[child["id"]] = idx

    for cid in CORE_IDS:
        node, depth = find_first(layout, lambda n: n.get("id") == cid if isinstance(n, dict) else False)
        if node is not None and depth is not None:
            pos_penalty = order_penalty * top_positions.get(cid, 5)
            score += max(0.0, 0.6 - depth_penalty * depth - pos_penalty)
    # Normalize roughly to 0..1
    return min(1.0, score / 1.8)


def compute_scroll_length(layout: Dict[str, Any]) -> float:
    """Estimate scroll length as count of history-related nodes."""
    count = 0
    for n, _ in traverse_nodes(layout):
        if not isinstance(n, dict):
            continue
        if n.get("id") == "history" or n.get("type") == "event":
            count += 1
    return float(count)


def compute_misoperation_risk(layout: Dict[str, Any]) -> float:
    """High if internal/external messages are not visually distinct."""
    has_internal = False
    has_external = False
    differentiated = False
    for n, _ in traverse_nodes(layout):
        if not isinstance(n, dict):
            continue
        if n.get("type") == "message":
            vis = n.get("visibility")
            if vis == "internal":
                has_internal = True
            if vis == "external":
                has_external = True
            if n.get("visual_tag") or n.get("style"):
                differentiated = True
    if has_internal and has_external and not differentiated:
        return 0.8
    if has_internal and has_external and differentiated:
        return 0.3
    return 0.5 if has_internal or has_external else 0.2


def compute_metrics(layout: Dict[str, Any]) -> Dict[str, float]:
    return {
        "hierarchy_clarity_score": round(compute_hierarchy_clarity(layout), 3),
        "scroll_length": round(compute_scroll_length(layout), 3),
        "misoperation_risk_score": round(compute_misoperation_risk(layout), 3),
    }
