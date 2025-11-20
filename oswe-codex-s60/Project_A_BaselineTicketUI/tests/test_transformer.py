import pytest
from pathlib import Path
import transformer


def get_scenario(scenarios, sid):
    for sc in scenarios:
        if sc.get("id") == sid:
            return sc
    return None


def test_transform_returns_expected_keys(scenarios):
    layout = scenarios[0]["initial_layout"]
    result = transformer.transform(layout, scenario_id=scenarios[0]["id"])
    assert set(result.keys()) >= {"scenario_id", "transformed_layout", "metrics", "ui_warnings", "edge_case_flags", "errors", "status"}


def test_baseline_clarity_not_improved(scenarios):
    sc = get_scenario(scenarios, "normal_overloaded_main_flow")
    result = transformer.transform(sc["initial_layout"], scenario_id=sc["id"])
    assert result["metrics"].get("hierarchy_clarity_score", 0) < 0.6


def test_baseline_misoperation_risk_not_reduced(scenarios):
    sc = get_scenario(scenarios, "mis_operation_internal_external_confusion")
    result = transformer.transform(sc["initial_layout"], scenario_id=sc["id"])
    assert result["metrics"].get("misoperation_risk_score", 0) >= 0.5


def test_baseline_handles_malformed_without_crash(scenarios):
    sc = get_scenario(scenarios, "malformed_input_with_unsafe_html")
    result = transformer.transform(sc["initial_layout"], scenario_id=sc["id"])
    assert result["status"] == "pass"
    assert "invalid_node" in result.get("ui_warnings", [])
