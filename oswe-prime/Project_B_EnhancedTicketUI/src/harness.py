import json
import os
import logging
import sys
from pathlib import Path

# Ensure local src path is on sys.path when executing harness directly
sys.path.append(str(Path(__file__).absolute().parent))
from transformer import EnhancedTransformer


log = logging.getLogger("enhanced_harness")


def run_scenarios(scenarios):
    results = []
    for s in scenarios:
        t = EnhancedTransformer(s.get("input_layout"))
        out = t.transform()
        expected = s.get("expected", {})
        status = "pass"
        # check core_on_top expected
        if expected.get("core_on_top"):
            # if hierarchy_clarity_score >= 66 treat as pass
            if out["metrics"].get("hierarchy_clarity_score", 0) < 66:
                status = "fail"
        if expected.get("timeline_collapsed"):
            # if collapsed_sections_count > 0 consider passed
            if out["metrics"].get("collapsed_sections_count", 0) == 0:
                status = "fail"
        if expected.get("preview_blocking") is False:
            # check attachments preview_mode (by type or label)
            found = False
            for f in out["output_layout"]["fields"]:
                if (f.get("type") == "attachments" or f.get("label") == "attachments"):
                    if f.get("ui", {}).get("preview_mode") == "side-panel":
                        found = True
            if not found:
                status = "fail"
        if expected.get("internal_clear"):
            # check any notes have internal flag true
            ok = False
            for f in out["output_layout"]["fields"]:
                if f.get("type") == "notes" and f.get("ui", {}).get("internal"):
                    ok = True
            if not ok:
                status = "fail"

        # Malformed input: check safe fallback
        if expected.get("safe_fallback"):
            if "unsafe_html_detected" not in out["ui_warnings"] and "invalid_field_type" not in out["errors"]:
                # baseline: if we didn't detect any of these errors, that's possibly a fail
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
    sp = Path(os.getenv("SCENARIO_PATH", Path(__file__).absolute().parents[2] / "shared" / "test_scenarios.json"))
    with open(sp, 'r', encoding='utf-8') as fh:
        scenarios = json.load(fh)

    results = run_scenarios(scenarios)
    outdir = Path(os.getenv("OUTPUT_DIR", Path(__file__).absolute().parents[1] / "results"))
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / 'results_post.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    with open(outdir / 'log_post.txt', 'w', encoding='utf-8') as f:
        for r in results:
            f.write(str(r) + '\n')
    print('Enhanced tests written to', outdir)
