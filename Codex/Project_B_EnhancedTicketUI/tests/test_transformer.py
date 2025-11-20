import json
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from transformer import TicketLayoutTransformer  # noqa: E402

SCENARIO_PATH = Path(os.environ["TEST_SCENARIOS_PATH"])
RESULTS_DIR = Path(os.environ["RESULTS_DIR"])
LOG_DIR = Path(os.environ["LOG_DIR"])
RESULT_KIND = os.environ.get("RESULT_KIND", "post")

with SCENARIO_PATH.open(encoding="utf-8") as handle:
    SCENARIOS = json.load(handle)

results_bucket = []
log_lines = []


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda item: item["id"])
def test_enhanced_behavior(scenario):
    transformer = TicketLayoutTransformer()
    result = transformer.transform(scenario["input_layout"])
    expected = scenario["expectations"]["enhanced"]

    assert result["status"] == expected["status"], scenario["id"]
    assert result["metrics"] == expected["metrics"], scenario["id"]
    assert sorted(result["ui_warnings"]) == sorted(expected["ui_warnings"]), scenario["id"]
    assert sorted(result["edge_case_flags"]) == sorted(expected["edge_case_flags"]), scenario["id"]
    assert sorted(result["errors"]) == sorted(expected["errors"]), scenario["id"]

    _validate_improvements(result, scenario)
    results_bucket.append({"id": scenario["id"], "result": result})
    log_lines.append(
        f"{scenario['id']}: clarity={result['metrics']['clarity_score']} "
        f"collapsed={result['metrics']['collapsed_sections']} "
        f"risk={result['metrics']['misoperation_risk']}"
    )


def _validate_improvements(result, scenario):
    layout = result["layout"]
    sections = layout.get("sections", [])
    assert sections, "core section should exist"
    assert sections[0].get("category") == "core"
    attachments_mode = layout.get("attachments", {}).get("mode")
    assert attachments_mode in {"inline", "side-panel"}
    if scenario["id"] in {"normal_flow", "long_scroll_flow", "complex_nesting"}:
        collapsed_histories = [
            sec for sec in sections if sec.get("category") in {"history", "logs", "related"}
        ]
        assert collapsed_histories, "history should be preserved"
        assert all(sec.get("collapsed") for sec in collapsed_histories)
    notes = layout.get("notes", [])
    if scenario["id"] in {"normal_flow", "mis_operation_flow"}:
        styles = {note.get("style") for note in notes}
        assert len(styles) >= 2
    if scenario["id"] == "malformed_input":
        assert "malformed-corrected" in result["edge_case_flags"]
        assert "html-neutralized" in result["edge_case_flags"]
    if scenario["id"] == "long_scroll_flow":
        assert result["metrics"]["scroll_savings"] > 30


def teardown_module(module):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    results_file = RESULTS_DIR / f"results_{RESULT_KIND}.json"
    log_file = LOG_DIR / f"log_{RESULT_KIND}.txt"
    with results_file.open("w", encoding="utf-8") as handle:
        json.dump(results_bucket, handle, indent=2)
    with log_file.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(log_lines))
