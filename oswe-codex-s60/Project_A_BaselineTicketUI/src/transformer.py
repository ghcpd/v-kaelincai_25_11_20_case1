import json
from typing import Any, Dict, List
try:
    from .utils import expand_repeats, traverse_nodes, sanitize_html, safe_get
    from .metrics import compute_metrics
except ImportError:  # pragma: no cover
    from utils import expand_repeats, traverse_nodes, sanitize_html, safe_get
    from metrics import compute_metrics


class BaselineTransformer:
    """Baseline: minimal processing, no UX improvements."""

    def transform(self, layout: Any, scenario_id: str = None) -> Dict[str, Any]:
        ui_warnings: List[str] = []
        errors: List[str] = []
        edge_case_flags: List[str] = []

        # Expand repeats and sanitize minimal HTML
        try:
            layout_expanded = expand_repeats(layout)
        except Exception as e:
            layout_expanded = layout
            errors.append(f"expand_repeats_failed: {e}")

        # Flag edge cases
        try:
            max_depth = 0
            for _, depth in traverse_nodes(layout_expanded):
                max_depth = max(max_depth, depth)
            if max_depth > 5:
                edge_case_flags.append("deep_nesting")
        except Exception:
            pass

        # Sanitize HTML at root keys if strings
        if isinstance(layout_expanded, dict):
            for key in ("content", "title"):
                if key in layout_expanded:
                    layout_expanded[key], sanitized = sanitize_html(layout_expanded[key])
                    if sanitized:
                        ui_warnings.append("sanitized_html")

        # Identify malformed nodes
        try:
            for n, _ in traverse_nodes(layout_expanded):
                if not isinstance(n, dict) and not isinstance(n, list):
                    ui_warnings.append("invalid_node")
                    break
        except Exception:
            pass

        metrics = compute_metrics(layout_expanded) if isinstance(layout_expanded, (dict, list)) else {}

        result = {
            "scenario_id": scenario_id,
            "transformed_layout": layout_expanded,
            "metrics": metrics,
            "ui_warnings": sorted(set(ui_warnings)),
            "edge_case_flags": sorted(set(edge_case_flags)),
            "errors": errors,
        }
        # Baseline doesn't enforce UX improvements; status reflects transform success
        result["status"] = "pass" if not errors else "fail"
        return result


def transform(layout: Any, scenario_id: str = None) -> Dict[str, Any]:
    return BaselineTransformer().transform(layout, scenario_id=scenario_id)


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Baseline Ticket UI transformer")
    parser.add_argument("--scenarios", type=str, required=True, help="Path to test_scenarios.json")
    parser.add_argument("--output", type=str, default="results_pre.json", help="Output results JSON")
    args = parser.parse_args()

    scenarios = json.loads(Path(args.scenarios).read_text(encoding="utf-8"))
    transformer = BaselineTransformer()
    outputs = []
    for scenario in scenarios:
        layout = scenario.get("initial_layout")
        sid = scenario.get("id")
        outputs.append(transformer.transform(layout, scenario_id=sid))
    Path(args.output).write_text(json.dumps(outputs, indent=2), encoding="utf-8")
    print(f"Wrote {args.output} with {len(outputs)} scenarios")
