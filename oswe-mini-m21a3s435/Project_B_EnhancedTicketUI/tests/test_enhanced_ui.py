import json
import os
from src.transform import enhanced_transform


def load_scenarios():
    p = os.path.join(os.path.dirname(__file__), "..", "test_scenarios.json")
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_enhanced_transforms_and_write_results():
    scenarios = load_scenarios()
    results = []
    logs = []

    outdir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(outdir, exist_ok=True)

    for s in scenarios:
        inp = s["input"]
        out = enhanced_transform(inp)
        expected = s.get("expected", {})

        passed = True
        if expected.get("metrics"):
            # check clarity score threshold
            if out.get("metrics", {}).get("hierarchy_clarity", 0) < expected["metrics"]["hierarchy_clarity"]:
                passed = False

        if expected.get("history_collapsed"):
            if not out["transformed"]["history"].get("collapsed"):
                passed = False

        if expected.get("warnings_contains"):
            if expected["warnings_contains"] not in out.get("warnings", []):
                passed = False

        if expected.get("transformed_core_keys"):
            for k in expected["transformed_core_keys"]:
                if k not in out["transformed"]["core"]:
                    passed = False

        results.append({"id": s["id"], "passed": passed, "output": out})
        logs.append(f"{s['id']}: passed={passed}")

    # produce a simple HTML mockup showing the core block
    if scenarios:
        first = enhanced_transform(scenarios[0]["input"])
        with open(os.path.join(outdir, "prototype_post.html"), "w", encoding="utf-8") as fh:
            fh.write("<html><body>")
            fh.write("<h1>Core</h1>")
            fh.write(f"<pre>{json.dumps(first['transformed']['core'])}</pre>")
            fh.write("</body></html>")

    agg = {"scenarios": len(results), "passed": sum(1 for r in results if r["passed"]), "results": results}
    with open(os.path.join(outdir, "results_post.json"), "w", encoding="utf-8") as fh:
        json.dump(agg, fh, indent=2)
    with open(os.path.join(outdir, "log_post.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(logs))

    assert len(results) >= 5
