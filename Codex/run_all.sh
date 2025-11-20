#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

pushd "$ROOT_DIR" >/dev/null
bash Project_A_BaselineTicketUI/run_tests.sh
bash Project_B_EnhancedTicketUI/run_tests.sh
popd >/dev/null

PYTHON_BIN="$(command -v python3 || command -v python)"
if [ -z "$PYTHON_BIN" ]; then
  echo "Python interpreter not found for aggregation." >&2
  exit 1
fi

"$PYTHON_BIN" <<'PY'
import json
from pathlib import Path

root = Path(__file__).resolve().parent
results_root = root / "results"
results_root.mkdir(exist_ok=True)

pre_path = root / "Project_A_BaselineTicketUI" / "results" / "results_pre.json"
post_path = root / "Project_B_EnhancedTicketUI" / "results" / "results_post.json"

with pre_path.open(encoding="utf-8") as handle:
    pre_results = {entry["id"]: entry["result"] for entry in json.load(handle)}
with post_path.open(encoding="utf-8") as handle:
    post_results = {entry["id"]: entry["result"] for entry in json.load(handle)}

scenario_summaries = []
for scenario_id, baseline_result in pre_results.items():
    enhanced_result = post_results[scenario_id]
    pre_metrics = baseline_result["metrics"]
    post_metrics = enhanced_result["metrics"]
    summary = {
        "id": scenario_id,
        "baseline_status": baseline_result["status"],
        "enhanced_status": enhanced_result["status"],
        "clarity_pre": pre_metrics["clarity_score"],
        "clarity_post": post_metrics["clarity_score"],
        "collapsed_pre": pre_metrics["collapsed_sections"],
        "collapsed_post": post_metrics["collapsed_sections"],
        "scroll_pre": pre_metrics["scroll_savings"],
        "scroll_post": post_metrics["scroll_savings"],
        "attachment_pre": pre_metrics["attachment_non_blocking"],
        "attachment_post": post_metrics["attachment_non_blocking"],
        "misoperation_pre": pre_metrics["misoperation_risk"],
        "misoperation_post": post_metrics["misoperation_risk"],
        "edge_case_flags_post": enhanced_result["edge_case_flags"],
        "ui_warnings_post": enhanced_result["ui_warnings"],
    }
    scenario_summaries.append(summary)

total = len(scenario_summaries)
avg_clarity_pre = sum(item["clarity_pre"] for item in scenario_summaries) / total
avg_clarity_post = sum(item["clarity_post"] for item in scenario_summaries) / total
avg_mis_pre = sum(item["misoperation_pre"] for item in scenario_summaries) / total
avg_mis_post = sum(item["misoperation_post"] for item in scenario_summaries) / total
scroll_gain = sum(item["scroll_post"] - item["scroll_pre"] for item in scenario_summaries)
collapsed_gain = sum(item["collapsed_post"] - item["collapsed_pre"] for item in scenario_summaries)
attachment_improvements = sum(
    (1 if (not item["attachment_pre"] and item["attachment_post"]) else 0)
    for item in scenario_summaries
)

summary_payload = {
    "total_scenarios": total,
    "average_clarity_pre": avg_clarity_pre,
    "average_clarity_post": avg_clarity_post,
    "average_misoperation_risk_pre": avg_mis_pre,
    "average_misoperation_risk_post": avg_mis_post,
    "total_scroll_savings_delta": scroll_gain,
    "total_collapsed_sections_delta": collapsed_gain,
    "attachment_preview_improvements": attachment_improvements,
    "scenarios": scenario_summaries,
}

(results_root / "compare_summary.json").write_text(
    json.dumps(summary_payload, indent=2), encoding="utf-8"
)

def format_bool(value: bool) -> str:
    return "✅" if value else "⚠️"

lines = []
lines.append("# SaaS Ticket Detail Comparison Report")
lines.append("")
lines.append(f"*Total scenarios:* {total}")
lines.append(
    f"*Average clarity:* {avg_clarity_pre:.1f} -> {avg_clarity_post:.1f} "
    f"(Δ {avg_clarity_post - avg_clarity_pre:.1f})"
)
lines.append(
    f"*Average mis-operation risk:* {avg_mis_pre:.1f} -> {avg_mis_post:.1f} "
    f"(Δ {avg_mis_post - avg_mis_pre:.1f})"
)
lines.append(f"*Total scroll savings delta:* {scroll_gain}")
lines.append(f"*Attachment preview improvements:* {attachment_improvements} / {total}")
lines.append("")
lines.append("## Pass / Fail Matrix")
lines.append("| Scenario | Baseline | Enhanced | Clarity Δ | Mis-operation Δ |")
lines.append("| --- | --- | --- | --- | --- |")
for item in scenario_summaries:
    lines.append(
        f"| {item['id']} | {item['baseline_status']} | {item['enhanced_status']} | "
        f"{item['clarity_post'] - item['clarity_pre']} | "
        f"{item['misoperation_post'] - item['misoperation_pre']} |"
    )

lines.append("")
lines.append("## Hierarchy Clarity")
lines.append(
    f"- Collapsed sections introduced in {collapsed_gain} areas; "
    f"core info now leads every scenario."
)
lines.append(
    "- Deeply nested layouts were flattened and regrouped, producing "
    "clarity boosts between "
    f"{min(item['clarity_post'] - item['clarity_pre'] for item in scenario_summaries)} "
    "and "
    f"{max(item['clarity_post'] - item['clarity_pre'] for item in scenario_summaries)} points."
)

lines.append("")
lines.append("## Collapsible Structures")
lines.append(
    f"- Scroll savings gained: {scroll_gain} units with "
    f"{sum(item['collapsed_post'] for item in scenario_summaries)} default-collapsed sections."
)
lines.append(
    "- Long history and complex nesting scenarios now ship collapsed timelines by default."
)

lines.append("")
lines.append("## Attachment Preview & Interaction Safety")
lines.append(
    f"- {attachment_improvements} scenarios switched from blocking overlays to non-blocking previews."
)
lines.append(
    "- Mis-operation confirmation prompts and note channel styling reduced risk by "
    f"{avg_mis_pre - avg_mis_post:.1f} points on average."
)

lines.append("")
lines.append("## Edge-case Handling")
for item in scenario_summaries:
    if item["edge_case_flags_post"]:
        warnings = item["ui_warnings_post"] or ["none"]
        lines.append(
            f"- {item['id']}: safeguards {', '.join(item['edge_case_flags_post'])} "
            f"with warnings {', '.join(warnings)}."
        )

(root / "compare_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

echo "Reports written to results/compare_summary.json and compare_report.md"
