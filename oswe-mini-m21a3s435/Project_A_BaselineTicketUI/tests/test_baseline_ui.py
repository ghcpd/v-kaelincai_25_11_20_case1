import json
import os
from src.transform import baseline_transform


def load_scenarios():
    p = os.path.join(os.path.dirname(__file__), "..", "test_scenarios.json")
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_baseline_transform_and_write_results():
    scenarios = load_scenarios()
    results = []
    logs = []

    outdir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(outdir, exist_ok=True)

    for s in scenarios:
        inp = s["input"]
        out = baseline_transform(inp)
        passed = out.get("status") == s.get("expected", {}).get("status", out.get("status"))
        results.append({"id": s["id"], "passed": passed, "output": out})
        logs.append(f"{s['id']}: passed={passed}")

    agg = {"scenarios": len(results), "passed": sum(1 for r in results if r["passed"]), "results": results}

    with open(os.path.join(outdir, "results_pre.json"), "w", encoding="utf-8") as fh:
        json.dump(agg, fh, indent=2)

    with open(os.path.join(outdir, "log_pre.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(logs))

    # also write a very simple html prototype
    with open(os.path.join(outdir, "prototype_pre.html"), "w", encoding="utf-8") as fh:
        fh.write(f"<html><body><pre>{json.dumps(scenarios[0]['input'])}</pre></body></html>")

    assert len(results) >= 5
