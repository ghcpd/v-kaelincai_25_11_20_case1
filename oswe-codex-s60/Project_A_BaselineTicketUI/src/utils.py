import copy
import json
import re
from typing import Any, Dict, List, Tuple


def deep_copy(obj: Any) -> Any:
    try:
        return copy.deepcopy(obj)
    except Exception:
        return json.loads(json.dumps(obj))


def sanitize_html(content: Any) -> Tuple[Any, bool]:
    """Naively strip <script> tags; return (sanitized_content, sanitized_flag)."""
    if not isinstance(content, str):
        return content, False
    sanitized = re.sub(r"<\s*script[^>]*>.*?<\s*/\s*script>", "", content, flags=re.IGNORECASE | re.DOTALL)
    return sanitized, sanitized != content


def expand_repeats(node: Any) -> Any:
    """Expand nodes with a 'repeat' count by duplicating their children."""
    if isinstance(node, dict):
        node = deep_copy(node)
        repeat = node.pop("repeat", None)
        if repeat and isinstance(repeat, int) and repeat > 1:
            if "children" in node and isinstance(node["children"], list) and node["children"]:
                orig_children = node["children"]
                expanded_children = []
                for i in range(repeat):
                    for child in orig_children:
                        child_copy = deep_copy(child)
                        # Replace placeholder # with index if present
                        if isinstance(child_copy, dict):
                            if "text" in child_copy and isinstance(child_copy["text"], str):
                                child_copy["text"] = child_copy["text"].replace("#", str(i + 1))
                        expanded_children.append(expand_repeats(child_copy))
                node["children"] = expanded_children
        # Recurse into children
        if "children" in node and isinstance(node["children"], list):
            node["children"] = [expand_repeats(c) for c in node["children"]]
        # Sanitize content fields
        for key in ("content", "title", "text"):
            if key in node:
                node[key], _ = sanitize_html(node[key])
        return node
    elif isinstance(node, list):
        return [expand_repeats(item) for item in node]
    else:
        return node


def traverse_nodes(node: Any, depth: int = 0):
    # Always yield the current node for detection purposes
    yield node, depth
    if isinstance(node, dict):
        for child in node.get("children", []) if isinstance(node.get("children"), list) else []:
            yield from traverse_nodes(child, depth + 1)
    elif isinstance(node, list):
        for item in node:
            yield from traverse_nodes(item, depth)


def find_first(node: Any, predicate):
    for n, d in traverse_nodes(node):
        try:
            if predicate(n):
                return n, d
        except Exception:
            continue
    return None, None


def safe_get(node: Dict, key: str, default=None):
    if isinstance(node, dict):
        return node.get(key, default)
    return default
