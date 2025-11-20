import json
import os
import logging
import sys
from pathlib import Path

# Ensure local src path is on sys.path when executing harness directly
sys.path.append(str(Path(__file__).absolute().parent))
from transformer import BaselineTransformer


log = logging.getLogger("baseline_harness")


def run_scenarios(scenarios):
    results = []
    for s in scenarios:
        t = BaselineTransformer(s.get("input_layout"))
        out = t.transform()
        # compute pass/fail for expected conditions
        expected = s.get("expected", {})
        status = "pass"
        # check core_on_top expected
        if expected.get("core_on_top"):
            # baseline likely fails: check if hierarchy clarity score > 50
            if out["metrics"].get("hierarchy_clarity_score", 0) < 50:
                status = "fail"
        # check internal differentiation
        if expected.get("internal_clear"):
            # baseline does not differentiate
            # If mis_operation risk is 0 then ok, else fail
            if out["metrics"].get("mis_operation_risk", 0) > 0:
                status = "fail"

        results.append({
            "id": s.get("id"),
            "status": out.get("status"),
            "pass": status == "pass",
            "metrics": out.get("metrics"),
            "ui_warnings": out.get("ui_warnings"),
            "errors": out.get("errors"),
            "output_layout": out.get("output_layout"),
        })
    return results


if __name__ == "__main__":
    scenarios_path = Path(__file__).absolute().parents[1] / ".." / "shared" / "test_scenarios.json"
    # above computed path might not be correct when running tests; we'll look relative
    sp = Path(os.getenv("SCENARIO_PATH", Path(__file__).absolute().parents[2] / "shared" / "test_scenarios.json"))
    with open(sp, 'r', encoding='utf-8') as fh:
        scenarios = json.load(fh)

    results = run_scenarios(scenarios)
    outdir = Path(os.getenv("OUTPUT_DIR", Path(__file__).absolute().parents[1] / "results"))
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / 'results_pre.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    with open(outdir / 'log_pre.txt', 'w', encoding='utf-8') as f:
        for r in results:
            f.write(str(r) + '\n')
    print('Baseline tests written to', outdir)
