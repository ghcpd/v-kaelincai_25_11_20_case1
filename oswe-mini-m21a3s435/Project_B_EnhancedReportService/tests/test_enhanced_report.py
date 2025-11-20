import json
import os
import time
from src.enhanced_service import EnhancedReportService


def load_scenarios():
    p = os.path.join(os.path.dirname(__file__), "..", "test_scenarios.json")
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_enhanced_paths_and_write_results(tmp_path):
    svc = EnhancedReportService()
    scenarios = load_scenarios()
    res = []
    logs = []

    outdir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(outdir, exist_ok=True)

    # warm the cache for a scenario
    svc.get_dimensions("day", ("region", "NA"))

    for s in scenarios:
        req = s["request"]
        # simulate peak: push cost threshold to low to simulate circuit
        if s["id"] == "peak_cost_circuit":
            svc._cost_threshold = 1

        start = time.time()
        if req.get("export"):
            out = svc.export(req)
        else:
            out = svc.query(req)
        lat = time.time() - start

        expected = s.get("expected", {})
        passed = True
        for k, v in expected.items():
            if isinstance(v, dict):
                # nested check
                if not all(out.get(k, {}).get(kk) == vv for kk, vv in v.items()):
                    passed = False
            else:
                if out.get(k) != v:
                    passed = False

        res.append({"id": s["id"], "latency": lat, "response": out, "passed": passed})
        logs.append(f"{s['id']}: {out} passed={passed}")

    agg = {"scenarios": len(res), "passed": sum(1 for r in res if r["passed"]), "results": res}

    with open(os.path.join(outdir, "results_post.json"), "w", encoding="utf-8") as fh:
        json.dump(agg, fh, indent=2)

    with open(os.path.join(outdir, "log_post.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(logs))

    assert len(res) >= 5
