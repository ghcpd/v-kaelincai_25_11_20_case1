from typing import Any, Dict
try:
    from .utils import traverse_nodes, find_first
except ImportError:  # pragma: no cover
    from utils import traverse_nodes, find_first

CORE_IDS = {"description", "priority", "status"}


def compute_hierarchy_clarity(layout: Dict[str, Any]) -> float:
    if not isinstance(layout, dict):
        return 0.0
    score = 0.0
    # Core block on top with emphasis
    children = layout.get("children") if isinstance(layout.get("children"), list) else []
    if children:
        first = children[0]
        if isinstance(first, dict) and first.get("type") == "core_info":
            score += 0.4
            if first.get("style", {}).get("emphasis"):
                score += 0.1
    # Each core field presence and shallow depth
    depth_penalty = 0.08
    order_bonus = 0.05
    for cid in CORE_IDS:
        node, depth = find_first(layout, lambda n: isinstance(n, dict) and n.get("id") == cid)
        if node is not None:
            score += max(0.0, 0.4 - depth_penalty * depth)
            # boost if inside core_info block
            parent_core, _ = find_first(layout, lambda n: isinstance(n, dict) and n.get("type") == "core_info" and any(isinstance(c, dict) and c.get("id") == cid for c in n.get("children", [])))
            if parent_core:
                score += order_bonus
    return min(1.0, score)


def compute_scroll_length(layout: Dict[str, Any]) -> float:
    """Effective scroll length factoring collapsed ancestry.

    - Collapsed history/log sections contribute a small constant (0.5)
    - Events inside collapsed sections contribute 0
    - Events in expanded sections contribute 1
    """

    def walk(node, collapsed_parent=False):
        total = 0.0
        if isinstance(node, dict):
            this_collapsed = collapsed_parent or (node.get("collapsible") and node.get("collapsed", False))
            # History/log container weight
            if node.get("id") in {"history", "logs", "related_tickets"}:
                total += 0.5 if node.get("collapsed", False) else 1.0
            # Event weight
            if node.get("type") == "event":
                total += 0.0 if this_collapsed else 1.0
            children = node.get("children", []) if isinstance(node.get("children"), list) else []
            for child in children:
                total += walk(child, this_collapsed)
        elif isinstance(node, list):
            for item in node:
                total += walk(item, collapsed_parent)
        return total

    return float(round(walk(layout, False), 3))


def compute_misoperation_risk(layout: Dict[str, Any]) -> float:
    has_internal = False
    has_external = False
    differentiated = False
    confirmations = False
    for n, _ in traverse_nodes(layout):
        if not isinstance(n, dict):
            continue
        if n.get("type") == "message":
            vis = n.get("visibility")
            if vis == "internal":
                has_internal = True
            if vis == "external":
                has_external = True
            if n.get("visual_tag") or (isinstance(n.get("style"), dict) and n["style"].get("variant")):
                differentiated = True
        if n.get("requires_confirmation"):
            confirmations = True
    if has_internal and has_external:
        if differentiated and confirmations:
            return 0.2
        if differentiated or confirmations:
            return 0.3
        return 0.7
    return 0.2 if confirmations else 0.3


def compute_attachment_usability(layout: Dict[str, Any]) -> float:
    """1.0 if all attachment previews are non-blocking."""
    blocking = 0
    total = 0
    for n, _ in traverse_nodes(layout):
        if not isinstance(n, dict):
            continue
        if n.get("attachments") and isinstance(n["attachments"], list):
            for att in n["attachments"]:
                if isinstance(att, dict):
                    total += 1
                    if att.get("preview_mode") == "overlay":
                        blocking += 1
    if total == 0:
        return 1.0
    return round(1.0 - blocking / total, 3)


def compute_metrics(layout: Dict[str, Any]) -> Dict[str, float]:
    return {
        "hierarchy_clarity_score": round(compute_hierarchy_clarity(layout), 3),
        "scroll_length": compute_scroll_length(layout),
        "misoperation_risk_score": round(compute_misoperation_risk(layout), 3),
        "attachment_usability_score": round(compute_attachment_usability(layout), 3),
    }
