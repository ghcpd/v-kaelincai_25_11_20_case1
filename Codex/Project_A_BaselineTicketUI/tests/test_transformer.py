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
RESULT_KIND = os.environ.get("RESULT_KIND", "pre")

with SCENARIO_PATH.open(encoding="utf-8") as handle:
    SCENARIOS = json.load(handle)

results_bucket = []
log_lines = []


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda item: item["id"])
def test_baseline_behavior(scenario):
    transformer = TicketLayoutTransformer()
    result = transformer.transform(scenario["input_layout"])
    expected = scenario["expectations"]["baseline"]

    assert result["status"] == expected["status"], scenario["id"]
    assert result["metrics"] == expected["metrics"], scenario["id"]
    assert sorted(result["ui_warnings"]) == sorted(expected["ui_warnings"]), scenario["id"]
    assert sorted(result["edge_case_flags"]) == sorted(expected["edge_case_flags"]), scenario["id"]
    assert sorted(result["errors"]) == sorted(expected["errors"]), scenario["id"]

    _validate_baseline_layout(result, scenario)
    results_bucket.append({"id": scenario["id"], "result": result})
    log_lines.append(
        f"{scenario['id']}: clarity={result['metrics']['clarity_score']} "
        f"collapsed={result['metrics']['collapsed_sections']} "
        f"risk={result['metrics']['misoperation_risk']}"
    )


def _validate_baseline_layout(result, scenario):
    layout = result["layout"]
    sections = layout.get("sections", [])
    if not sections:
        return
    core_first = sections[0].get("category") == "core"
    # Baseline should fail to surface the core information in most cases.
    if scenario["id"] != "mis_operation_flow":
        assert not core_first
    attachments_mode = layout.get("attachments", {}).get("mode", "fullscreen")
    if scenario["id"] in {"normal_flow", "long_scroll_flow", "complex_nesting", "malformed_input"}:
        assert attachments_mode == "fullscreen"
    notes = layout.get("notes", [])
    if len(notes) >= 2:
        styles = {note.get("style") for note in notes}
        assert len(styles) <= 1


def teardown_module(module):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    results_file = RESULTS_DIR / f"results_{RESULT_KIND}.json"
    log_file = LOG_DIR / f"log_{RESULT_KIND}.txt"
    with results_file.open("w", encoding="utf-8") as handle:
        json.dump(results_bucket, handle, indent=2)
    with log_file.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(log_lines))
