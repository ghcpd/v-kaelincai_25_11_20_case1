import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "Project_A_BaselineTicketUI" / "results" / "results_pre.json"
ENHANCED_PATH = ROOT / "Project_B_EnhancedTicketUI" / "results" / "results_post.json"
OUTPUT_DIR = ROOT / "results"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_json(path: Path):
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def compute_summary(entries, key):
    vals = []
    for e in entries:
        v = e.get("metrics", {}).get(key)
        if isinstance(v, (int, float)):
            vals.append(v)
    return mean(vals) if vals else None


def main():
    baseline = load_json(BASELINE_PATH)
    enhanced = load_json(ENHANCED_PATH)

    # Index by scenario_id
    b_idx = {e.get("scenario_id"): e for e in baseline}
    e_idx = {e.get("scenario_id"): e for e in enhanced}
    scenario_ids = sorted(set(b_idx.keys()) | set(e_idx.keys()))

    matrix_lines = ["| Scenario | Baseline Status | Enhanced Status | Δ Clarity | Δ Scroll | Δ Mis-op Risk |",
                    "|----------|-----------------|-----------------|----------:|---------:|--------------:|"]
    for sid in scenario_ids:
        b = b_idx.get(sid, {})
        e = e_idx.get(sid, {})
        bc = b.get("metrics", {}).get("hierarchy_clarity_score")
        ec = e.get("metrics", {}).get("hierarchy_clarity_score")
        bs = b.get("metrics", {}).get("scroll_length")
        es = e.get("metrics", {}).get("scroll_length")
        br = b.get("metrics", {}).get("misoperation_risk_score")
        er = e.get("metrics", {}).get("misoperation_risk_score")
        matrix_lines.append(
            f"| {sid} | {b.get('status','')} | {e.get('status','')} | "
            f"{_delta(bc, ec)} | {_delta(bs, es, invert=True)} | {_delta(br, er, invert=True)} |"
        )

    # Aggregates
    aggregates = {
        "baseline": {
            "avg_clarity": compute_summary(baseline, "hierarchy_clarity_score"),
            "avg_scroll": compute_summary(baseline, "scroll_length"),
            "avg_misop": compute_summary(baseline, "misoperation_risk_score"),
        },
        "enhanced": {
            "avg_clarity": compute_summary(enhanced, "hierarchy_clarity_score"),
            "avg_scroll": compute_summary(enhanced, "scroll_length"),
            "avg_misop": compute_summary(enhanced, "misoperation_risk_score"),
        },
    }

    report_lines = [
        "# Comparison Report",
        "",
        "## Pass/Fail Matrix",
        "\n".join(matrix_lines),
        "",
        "## Averages",
        f"- Baseline clarity: {aggregates['baseline']['avg_clarity']}",
        f"- Enhanced clarity: {aggregates['enhanced']['avg_clarity']}",
        f"- Baseline scroll length: {aggregates['baseline']['avg_scroll']}",
        f"- Enhanced scroll length: {aggregates['enhanced']['avg_scroll']}",
        f"- Baseline mis-op risk: {aggregates['baseline']['avg_misop']}",
        f"- Enhanced mis-op risk: {aggregates['enhanced']['avg_misop']}",
        "",
        "## Highlights",
        "- Hierarchy clarity delta should be positive (higher is better)",
        "- Scroll length delta should be negative (lower is better)",
        "- Mis-operation risk delta should be negative (lower is better)",
    ]

    (OUTPUT_DIR / "compare_report.md").write_text("\n".join(report_lines), encoding="utf-8")
    # Save combined results
    combined = {"baseline": baseline, "enhanced": enhanced, "aggregates": aggregates}
    (OUTPUT_DIR / "combined_results.json").write_text(json.dumps(combined, indent=2), encoding="utf-8")
    print("Comparison report generated at results/compare_report.md")


def _delta(b, e, invert=False):
    if b is None or e is None:
        return "n/a"
    diff = e - b
    if invert:
        diff = -diff
    return f"{diff:+.3f}"


if __name__ == "__main__":
    main()
