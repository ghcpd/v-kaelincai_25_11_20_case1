import json
import os
import time
from src.report_service import BaselineReportService


def load_scenarios():
    p = os.path.join(os.path.dirname(__file__), "..", "test_scenarios.json")
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def test_run_all_and_write_results(tmp_path):
    svc = BaselineReportService()
    scenarios = load_scenarios()
    results = []
    logs = []

    outdir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(outdir, exist_ok=True)

    for s in scenarios:
        req = s["request"]
        start = time.time()
        resp = svc.get_report(req)
        lat = time.time() - start

        passed = resp.get("status") == s.get("expected", {}).get("status", resp.get("status"))

        # if expected had edge case flags for stale data and we simulated freshness > 6h, mark
        ec_flags = []
        if s.get("initial_state", {}).get("freshness_lag_hours", 0) > 6:
            ec_flags.append("stale_data")

        entry = {
            "id": s["id"],
            "latency": lat,
            "status": resp.get("status"),
            "cache_hit": resp.get("cache_hit", False),
            "passed": bool(passed),
            "edge_case_flags": ec_flags,
        }
        results.append(entry)
        logs.append(f"{s['id']}: latency={lat:.3f}s status={resp.get('status')} passed={passed}")

    # summary
    total = len(results)
    passed = sum(1 for r in results if r["passed"])

    agg = {
        "scenarios": total,
        "passed": passed,
        "results": results,
    }

    with open(os.path.join(outdir, "results_pre.json"), "w", encoding="utf-8") as fh:
        json.dump(agg, fh, indent=2)

    with open(os.path.join(outdir, "log_pre.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(logs))

    assert total >= 5
