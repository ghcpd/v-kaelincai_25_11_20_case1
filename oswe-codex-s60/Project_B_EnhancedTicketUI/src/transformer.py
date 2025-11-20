import json
from typing import Any, Dict, List
try:
    from .utils import expand_repeats, traverse_nodes, sanitize_html, deep_copy
    from .metrics import compute_metrics
except ImportError:  # pragma: no cover
    from utils import expand_repeats, traverse_nodes, sanitize_html, deep_copy
    from metrics import compute_metrics

CORE_IDS = {"description", "priority", "status"}
COLLAPSIBLE_IDS = {"history", "logs", "related_tickets"}
CRITICAL_ACTIONS = {"send_reply", "change_status", "delete_ticket", "post_internal_note"}


class EnhancedTransformer:
    def transform(self, layout: Any, scenario_id: str = None) -> Dict[str, Any]:
        ui_warnings: List[str] = []
        errors: List[str] = []
        edge_case_flags: List[str] = []

        # Sanitize first to capture warnings before expansion modifies content
        try:
            sanitized_input = deep_copy(layout)
            self._sanitize_in_place(sanitized_input, ui_warnings)
        except Exception as e:
            sanitized_input = layout
            errors.append(f"sanitize_failed: {e}")

        try:
            working = expand_repeats(sanitized_input)
        except Exception as e:
            working = sanitized_input
            errors.append(f"expand_repeats_failed: {e}")

        # Normalize non-dict root
        if not isinstance(working, dict):
            ui_warnings.append("root_not_dict")
            working = {"type": "page", "children": working if isinstance(working, list) else []}

        # Edge case detection
        try:
            max_depth = 0
            history_count = 0
            for n, depth in traverse_nodes(working):
                max_depth = max(max_depth, depth)
                if isinstance(n, dict) and (n.get("id") == "history"):
                    history_children = n.get("children", []) if isinstance(n.get("children"), list) else []
                    history_count += len(history_children)
            if max_depth > 5:
                edge_case_flags.append("deep_nesting")
            if history_count > 10:
                edge_case_flags.append("long_history")
        except Exception:
            pass

        # malformed detection
        if any(w in ui_warnings for w in ("invalid_node", "root_not_dict")):
            edge_case_flags.append("malformed")

        try:
            transformed = self._apply_transformations(working, ui_warnings)
        except Exception as e:
            transformed = working
            errors.append(f"transform_failed: {e}")

        metrics = compute_metrics(transformed) if isinstance(transformed, dict) else {}

        result = {
            "scenario_id": scenario_id,
            "transformed_layout": transformed,
            "metrics": metrics,
            "ui_warnings": sorted(set(ui_warnings)),
            "edge_case_flags": sorted(set(edge_case_flags)),
            "errors": errors,
        }
        result["status"] = "pass" if not errors else "fail"
        return result

    # --- Internal helpers ---

    def _sanitize_in_place(self, node: Any, warnings: List[str]):
        if isinstance(node, dict):
            for key in ("content", "title", "text"):
                if key in node:
                    node[key], sanitized = sanitize_html(node[key])
                    if sanitized:
                        warnings.append("sanitized_html")
            # Recurse
            for child in node.get("children", []) if isinstance(node.get("children"), list) else []:
                self._sanitize_in_place(child, warnings)
        elif isinstance(node, list):
            for item in node:
                self._sanitize_in_place(item, warnings)
        else:
            warnings.append("invalid_node")

    def _apply_transformations(self, layout: Dict[str, Any], warnings: List[str]):
        layout = deep_copy(layout)
        # 1) Lift core info to top
        core_block = self._build_core_block(layout)
        if core_block:
            children = layout.get("children", []) if isinstance(layout.get("children"), list) else []
            children = [core_block] + [c for c in children if not (isinstance(c, dict) and c.get("type") == "core_info")]
            layout["children"] = children
        # 2) Collapsible sections
        self._apply_collapsible(layout)
        # 3) Optimize attachments
        self._optimize_attachments(layout)
        # 4) Differentiate messages
        self._differentiate_messages(layout)
        # 5) Confirmation prompts
        self._add_confirmation_prompts(layout)
        # 6) Group history (lightweight tagging)
        self._tag_history_groups(layout)
        return layout

    def _build_core_block(self, layout: Dict[str, Any]):
        collected = []
        def collect(node, parent):
            if not isinstance(node, dict):
                return
            if node.get("id") in CORE_IDS:
                collected.append(node)
                if parent and isinstance(parent, dict) and "children" in parent and isinstance(parent["children"], list):
                    try:
                        parent["children"].remove(node)
                    except ValueError:
                        pass
            for child in node.get("children", []) if isinstance(node.get("children"), list) else []:
                collect(child, node)
        collect(layout, None)
        if not collected:
            return None
        # Ensure ordering: description, priority, status
        order = {"description": 0, "priority": 1, "status": 2}
        collected.sort(key=lambda n: order.get(n.get("id"), 99))
        for item in collected:
            if isinstance(item, dict):
                item.setdefault("style", {})
                item["style"].update({"variant": "key", "emphasis": True})
        core_block = {
            "type": "core_info",
            "title": "Ticket Overview",
            "style": {"variant": "panel", "emphasis": True},
            "children": collected,
        }
        return core_block

    def _apply_collapsible(self, layout: Dict[str, Any]):
        for n, _ in traverse_nodes(layout):
            if not isinstance(n, dict):
                continue
            if n.get("id") in COLLAPSIBLE_IDS:
                n["collapsible"] = True
                n["collapsed"] = True
                children = n.get("children", []) if isinstance(n.get("children"), list) else []
                n["summary"] = {"item_count": len(children)}

    def _optimize_attachments(self, layout: Dict[str, Any]):
        for n, _ in traverse_nodes(layout):
            if not isinstance(n, dict):
                continue
            if n.get("attachments") and isinstance(n["attachments"], list):
                for att in n["attachments"]:
                    if isinstance(att, dict):
                        if att.get("preview_mode") == "overlay":
                            att["preview_mode"] = "side-panel"
                        att.setdefault("non_blocking", True)

    def _differentiate_messages(self, layout: Dict[str, Any]):
        for n, _ in traverse_nodes(layout):
            if not isinstance(n, dict):
                continue
            if n.get("type") == "message":
                vis = n.get("visibility")
                n.setdefault("style", {})
                if vis == "internal":
                    n["visual_tag"] = "Internal Note"
                    n["style"].update({"variant": "subtle", "color": "yellow"})
                elif vis == "external":
                    n["visual_tag"] = "Customer Reply"
                    n["style"].update({"variant": "accent", "color": "blue"})

    def _add_confirmation_prompts(self, layout: Dict[str, Any]):
        for n, _ in traverse_nodes(layout):
            if not isinstance(n, dict):
                continue
            if n.get("type") == "action" and n.get("action_type") in CRITICAL_ACTIONS:
                n["requires_confirmation"] = True
                n["confirmation_message"] = f"Are you sure you want to {n.get('action_type').replace('_', ' ')}?"

    def _tag_history_groups(self, layout: Dict[str, Any]):
        for n, _ in traverse_nodes(layout):
            if not isinstance(n, dict):
                continue
            if n.get("id") == "history" and isinstance(n.get("children"), list):
                # Simple grouping by subtype
                groups = {}
                for child in n["children"]:
                    if isinstance(child, dict):
                        key = child.get("subtype", "other")
                        groups.setdefault(key, []).append(child)
                n["grouped_by"] = list(groups.keys())


def transform(layout: Any, scenario_id: str = None) -> Dict[str, Any]:
    return EnhancedTransformer().transform(layout, scenario_id=scenario_id)


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Enhanced Ticket UI transformer")
    parser.add_argument("--scenarios", type=str, required=True, help="Path to test_scenarios.json")
    parser.add_argument("--output", type=str, default="results_post.json", help="Output results JSON")
    args = parser.parse_args()

    scenarios = json.loads(Path(args.scenarios).read_text(encoding="utf-8"))
    transformer = EnhancedTransformer()
    outputs = []
    for scenario in scenarios:
        layout = scenario.get("initial_layout")
        sid = scenario.get("id")
        outputs.append(transformer.transform(layout, scenario_id=sid))
    Path(args.output).write_text(json.dumps(outputs, indent=2), encoding="utf-8")
    print(f"Wrote {args.output} with {len(outputs)} scenarios")
