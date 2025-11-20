import pytest
import transformer
from utils import traverse_nodes


def get_scenario(scenarios, sid):
    for sc in scenarios:
        if sc.get("id") == sid:
            return sc
    return None


def test_core_info_lifted_and_highlighted(scenarios):
    sc = get_scenario(scenarios, "normal_overloaded_main_flow")
    result = transformer.transform(sc["initial_layout"], scenario_id=sc["id"])
    layout = result["transformed_layout"]
    children = layout.get("children", []) if isinstance(layout, dict) else []
    assert children and children[0].get("type") == "core_info"
    assert result["metrics"].get("hierarchy_clarity_score", 0) >= 0.7


def test_history_collapsed_and_summary(scenarios):
    sc = get_scenario(scenarios, "normal_overloaded_main_flow")
    result = transformer.transform(sc["initial_layout"], scenario_id=sc["id"])
    history = None
    for child in transformer.traverse_nodes(result["transformed_layout"]):
        pass
    # Walk manually to find history
    def find_history(node):
        if isinstance(node, dict) and node.get("id") == "history":
            return node
        for child in node.get("children", []) if isinstance(node, dict) and isinstance(node.get("children"), list) else []:
            found = find_history(child)
            if found:
                return found
        return None
    history = find_history(result["transformed_layout"])
    assert history is not None
    assert history.get("collapsible") is True
    assert history.get("collapsed") is True
    assert result["metrics"].get("scroll_length", 99) < 3


def test_attachment_preview_non_blocking(scenarios):
    sc = get_scenario(scenarios, "normal_overloaded_main_flow")
    result = transformer.transform(sc["initial_layout"], scenario_id=sc["id"])
    # Ensure no overlay preview modes remain
    for n, _ in traverse_nodes(result["transformed_layout"]):
        if isinstance(n, dict) and n.get("attachments"):
            for att in n["attachments"]:
                assert att.get("preview_mode") != "overlay"
    assert result["metrics"].get("attachment_usability_score", 0) == 1.0


def test_misoperation_prevention(scenarios):
    sc = get_scenario(scenarios, "mis_operation_internal_external_confusion")
    result = transformer.transform(sc["initial_layout"], scenario_id=sc["id"])
    layout = result["transformed_layout"]
    # Messages are visually tagged
    def message_tags(node):
        tags = []
        if isinstance(node, dict) and node.get("type") == "message":
            tags.append(node.get("visual_tag"))
        for child in node.get("children", []) if isinstance(node, dict) and isinstance(node.get("children"), list) else []:
            tags.extend(message_tags(child))
        return tags
    tags = message_tags(layout)
    assert "Internal Note" in tags and "Customer Reply" in tags
    # Actions require confirmation
    def confirmations(node):
        flags = []
        if isinstance(node, dict) and node.get("type") == "action":
            flags.append(node.get("requires_confirmation", False))
        for child in node.get("children", []) if isinstance(node, dict) and isinstance(node.get("children"), list) else []:
            flags.extend(confirmations(child))
        return flags
    assert any(confirmations(layout))
    assert result["metrics"].get("misoperation_risk_score", 1) <= 0.3


def test_long_history_collapsed_flagged(scenarios):
    sc = get_scenario(scenarios, "long_scroll_history")
    result = transformer.transform(sc["initial_layout"], scenario_id=sc["id"])
    assert "long_history" in result.get("edge_case_flags", [])
    assert result["metrics"].get("scroll_length", 99) < 5


def test_malformed_handled_and_sanitized(scenarios):
    sc = get_scenario(scenarios, "malformed_input_with_unsafe_html")
    result = transformer.transform(sc["initial_layout"], scenario_id=sc["id"])
    assert result["status"] == "pass"
    assert "malformed" in result.get("edge_case_flags", [])
    assert "sanitized_html" in result.get("ui_warnings", [])
    # Ensure no script tag remains
    def contains_script(node):
        if isinstance(node, dict):
            for key in ("content", "text", "title"):
                if key in node and isinstance(node[key], str) and "<script" in node[key].lower():
                    return True
            for child in node.get("children", []) if isinstance(node.get("children"), list) else []:
                if contains_script(child):
                    return True
        return False
    assert contains_script(result["transformed_layout"]) is False
