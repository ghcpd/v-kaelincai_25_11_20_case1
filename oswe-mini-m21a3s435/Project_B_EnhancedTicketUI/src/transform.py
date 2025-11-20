import html
import re
from typing import Dict, Any


def _sanitize_html(payload: str) -> str:
    # naive sanitizer: remove script tags and on* attributes
    no_scripts = re.sub(r"<script.*?>.*?</script>", "", payload, flags=re.I | re.S)
    # remove on<event>= handlers
    clean = re.sub(r"on\w+\s*=\s*\".*?\"", "", no_scripts, flags=re.I)
    return html.escape(clean)


def enhanced_transform(layout: Dict[str, Any]) -> Dict[str, Any]:
    out = {"status": "ok", "transformed": {}, "warnings": [], "metrics": {}}

    # Core info: pick up description, priority, status
    core_keys = ["description", "priority", "status"]
    core = {}
    for k in core_keys:
        if k in layout:
            val = layout[k]
            if isinstance(val, str) and "<script" in val.lower():
                out["warnings"].append("unsafe_html_cleaned")
                val = _sanitize_html(val)
            core[k] = val

    out["transformed"]["core"] = core

    # collapse history/log sections
    history = layout.get("history", [])
    if len(history) > 10:
        out["transformed"]["history"] = {"collapsed": True, "count": len(history), "preview": history[:3]}
    else:
        out["transformed"]["history"] = {"collapsed": False, "items": history}

    # attachments: provide non-blocking side-panel mode
    attachments = layout.get("attachments", [])
    att_panel = []
    for a in attachments:
        att_panel.append({"id": a.get("id"), "preview_mode": "side_panel"})
    out["transformed"]["attachments"] = att_panel

    # differentiate internal vs public notes
    notes = layout.get("notes", [])
    formatted_notes = []
    for n in notes:
        t = n.get("type")
        formatted_notes.append({"text": n.get("text"), "type": t, "ui_tag": "internal" if t == "internal" else "public"})
    out["transformed"]["notes"] = formatted_notes

    # provide mis-operation prevention metadata
    out["transformed"]["actions"] = {
        "close_ticket": {"confirmation_required": True, "message": "Confirm close?"},
        "delete_attachment": {"confirmation_required": True, "message": "Delete attachment permanently?"},
    }

    # handle badly formed nested structures gracefully
    try:
        # flatten deep tree if present
        tree = layout.get("tree")
        if isinstance(tree, dict):
            # shallow flatten up to 3 levels
            flat = {}
            def walk(dct, prefix=""):
                for k, v in dct.items():
                    if isinstance(v, dict) and prefix.count("/") < 3:
                        walk(v, prefix + k + "/")
                    else:
                        flat[prefix + k] = v
            walk(tree)
            out["transformed"]["flattened_tree"] = flat
    except Exception:
        out["warnings"].append("tree_flatten_failed")

    # metrics for hierarchy clarity: core present at top, history collapsed reduces scroll
    clarity_score = 0
    if out["transformed"]["core"]:
        clarity_score += 50
    if out["transformed"]["history"].get("collapsed"):
        clarity_score += 30
    if attachments:
        clarity_score += 10
    out["metrics"]["hierarchy_clarity"] = clarity_score

    return out
