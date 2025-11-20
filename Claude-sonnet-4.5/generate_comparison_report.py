"""
Generate comparison report between baseline and enhanced implementations.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


def load_results(filepath: str) -> Dict[str, Any]:
    """Load results from JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return {}


def calculate_improvement(baseline_val: float, enhanced_val: float, higher_is_better: bool = True) -> Dict[str, Any]:
    """Calculate improvement metrics."""
    if higher_is_better:
        delta = enhanced_val - baseline_val
        percent_change = ((enhanced_val - baseline_val) / baseline_val * 100) if baseline_val != 0 else 0
    else:
        # For metrics like mis_operation_risk, lower is better
        delta = baseline_val - enhanced_val
        percent_change = ((baseline_val - enhanced_val) / baseline_val * 100) if baseline_val != 0 else 0
    
    return {
        "baseline": baseline_val,
        "enhanced": enhanced_val,
        "delta": round(delta, 2),
        "percent_change": round(percent_change, 1)
    }


def generate_markdown_report(baseline_results: Dict[str, Any], enhanced_results: Dict[str, Any]) -> str:
    """Generate markdown comparison report."""
    report = []
    
    # Header
    report.append("# UI/UX Improvement Evaluation Report")
    report.append("## SaaS Ticket Detail Page Overload & Interaction Inefficiency")
    report.append("")
    report.append(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("---")
    report.append("")
    
    # Executive Summary
    report.append("## Executive Summary")
    report.append("")
    
    baseline_summary = baseline_results.get("summary", {})
    enhanced_summary = enhanced_results.get("summary", {})
    
    baseline_metrics = baseline_results.get("average_metrics", {})
    enhanced_metrics = enhanced_results.get("average_metrics", {})
    
    report.append("This report compares the **Baseline Ticket UI** (Project A) against the **Enhanced Ticket UI** (Project B) ")
    report.append("to evaluate improvements in information hierarchy, scroll reduction, and mis-operation prevention.")
    report.append("")
    
    # Test Execution Summary
    report.append("### Test Execution Summary")
    report.append("")
    report.append("| Metric | Baseline (Project A) | Enhanced (Project B) |")
    report.append("|--------|---------------------|---------------------|")
    report.append(f"| Total Scenarios | {baseline_summary.get('total_scenarios', 0)} | {enhanced_summary.get('total_scenarios', 0)} |")
    report.append(f"| Passed | {baseline_summary.get('passed', 0)} | {enhanced_summary.get('passed', 0)} |")
    report.append(f"| Failed | {baseline_summary.get('failed', 0)} | {enhanced_summary.get('failed', 0)} |")
    report.append(f"| Partial Success | {baseline_summary.get('partial_success', 0)} | {enhanced_summary.get('partial_success', 0)} |")
    report.append(f"| Edge Cases Covered | {baseline_summary.get('edge_cases_covered', 0)} | {enhanced_summary.get('edge_cases_covered', 0)} |")
    report.append(f"| Total Errors | {baseline_summary.get('total_errors', 0)} | {enhanced_summary.get('total_errors', 0)} |")
    report.append(f"| Total Warnings | {baseline_summary.get('total_warnings', 0)} | {enhanced_summary.get('total_warnings', 0)} |")
    report.append("")
    
    # Key Metrics Comparison
    report.append("---")
    report.append("")
    report.append("## Key Metrics Comparison")
    report.append("")
    
    # Hierarchy Clarity Score
    hierarchy_improvement = calculate_improvement(
        baseline_metrics.get("hierarchy_clarity_score", 0),
        enhanced_metrics.get("hierarchy_clarity_score", 0),
        higher_is_better=True
    )
    
    report.append("### 1. Hierarchy Clarity Score")
    report.append("")
    report.append("Measures how well core information (problem description, priority, status) is emphasized and positioned.")
    report.append("")
    report.append(f"- **Baseline:** {hierarchy_improvement['baseline']}")
    report.append(f"- **Enhanced:** {hierarchy_improvement['enhanced']}")
    report.append(f"- **Improvement:** +{hierarchy_improvement['delta']} ({hierarchy_improvement['percent_change']:+.1f}%)")
    report.append("")
    
    if hierarchy_improvement['percent_change'] > 50:
        report.append("✅ **Significant improvement** in visual hierarchy and information structure.")
    elif hierarchy_improvement['percent_change'] > 20:
        report.append("✅ **Moderate improvement** in visual hierarchy.")
    else:
        report.append("⚠️ **Limited improvement** in visual hierarchy.")
    report.append("")
    
    # Scroll Length Reduction
    scroll_improvement = calculate_improvement(
        baseline_metrics.get("scroll_length_reduction", 0),
        enhanced_metrics.get("scroll_length_reduction", 0),
        higher_is_better=True
    )
    
    report.append("### 2. Scroll Length Reduction")
    report.append("")
    report.append("Measures reduction in page scroll length through collapsible sections and optimized layout.")
    report.append("")
    report.append(f"- **Baseline:** {scroll_improvement['baseline']} (no reduction)")
    report.append(f"- **Enhanced:** {scroll_improvement['enhanced']}")
    report.append(f"- **Improvement:** +{scroll_improvement['delta']} ({scroll_improvement['percent_change']:+.1f}%)")
    report.append("")
    
    if enhanced_metrics.get("scroll_length_reduction", 0) >= 0.5:
        report.append("✅ **Excellent scroll reduction** - 50%+ reduction in scroll length.")
    elif enhanced_metrics.get("scroll_length_reduction", 0) >= 0.3:
        report.append("✅ **Good scroll reduction** - 30%+ reduction in scroll length.")
    else:
        report.append("⚠️ **Moderate scroll reduction** achieved.")
    report.append("")
    
    # Mis-operation Risk
    misop_improvement = calculate_improvement(
        baseline_metrics.get("mis_operation_risk", 1.0),
        enhanced_metrics.get("mis_operation_risk", 1.0),
        higher_is_better=False  # Lower is better
    )
    
    report.append("### 3. Mis-operation Risk")
    report.append("")
    report.append("Measures risk of user errors (e.g., sending internal notes to customers). Lower is better.")
    report.append("")
    report.append(f"- **Baseline:** {misop_improvement['baseline']} (high risk)")
    report.append(f"- **Enhanced:** {misop_improvement['enhanced']}")
    report.append(f"- **Reduction:** -{misop_improvement['delta']} ({misop_improvement['percent_change']:+.1f}% reduction)")
    report.append("")
    
    if misop_improvement['percent_change'] > 70:
        report.append("✅ **Substantial risk reduction** - clear visual distinctions implemented.")
    elif misop_improvement['percent_change'] > 40:
        report.append("✅ **Good risk reduction** - improved safety mechanisms.")
    else:
        report.append("⚠️ **Limited risk reduction** - more safety measures recommended.")
    report.append("")
    
    # Scenario-by-Scenario Analysis
    report.append("---")
    report.append("")
    report.append("## Scenario-by-Scenario Analysis")
    report.append("")
    
    baseline_results_list = baseline_results.get("results", [])
    enhanced_results_list = enhanced_results.get("results", [])
    
    for i, (baseline_result, enhanced_result) in enumerate(zip(baseline_results_list, enhanced_results_list), 1):
        scenario_name = baseline_result.get("scenario_name", f"Scenario {i}")
        scenario_id = baseline_result.get("scenario_id", "")
        
        report.append(f"### Scenario {i}: {scenario_name}")
        report.append(f"**ID:** `{scenario_id}`")
        report.append("")
        
        baseline_status = baseline_result.get("test_status", "unknown")
        enhanced_status = enhanced_result.get("test_status", "unknown")
        
        report.append(f"| Aspect | Baseline | Enhanced |")
        report.append(f"|--------|----------|----------|")
        report.append(f"| Test Status | {baseline_status} | {enhanced_status} |")
        
        baseline_metrics_scenario = baseline_result.get("actual_output", {}).get("metrics", {})
        enhanced_metrics_scenario = enhanced_result.get("actual_output", {}).get("metrics", {})
        
        report.append(f"| Hierarchy Clarity | {baseline_metrics_scenario.get('hierarchy_clarity_score', 0)} | {enhanced_metrics_scenario.get('hierarchy_clarity_score', 0)} |")
        report.append(f"| Scroll Reduction | {baseline_metrics_scenario.get('scroll_length_reduction', 0)} | {enhanced_metrics_scenario.get('scroll_length_reduction', 0)} |")
        report.append(f"| Mis-op Risk | {baseline_metrics_scenario.get('mis_operation_risk', 0)} | {enhanced_metrics_scenario.get('mis_operation_risk', 0)} |")
        report.append("")
        
        # Behavioral improvements
        enhanced_behavior = enhanced_result.get("validation_details", {}).get("behavior_validation", {})
        met_expectations = enhanced_behavior.get("met_expectations", [])
        unmet_expectations = enhanced_behavior.get("unmet_expectations", [])
        
        if met_expectations:
            report.append("**Enhanced Improvements:**")
            for expectation in met_expectations[:5]:  # Show top 5
                report.append(f"- ✅ {expectation}")
            report.append("")
        
        if unmet_expectations:
            report.append("**Remaining Issues:**")
            for expectation in unmet_expectations[:3]:  # Show top 3
                report.append(f"- ⚠️ {expectation}")
            report.append("")
        
        report.append("")
    
    # Edge Case Handling
    report.append("---")
    report.append("")
    report.append("## Edge Case Handling")
    report.append("")
    
    report.append("| Edge Case Category | Baseline | Enhanced | Status |")
    report.append("|--------------------|----------|----------|--------|")
    
    # Collect all edge case flags
    baseline_flags = set()
    enhanced_flags = set()
    
    for result in baseline_results_list:
        flags = result.get("actual_output", {}).get("edge_case_flags", [])
        baseline_flags.update(flags)
    
    for result in enhanced_results_list:
        flags = result.get("actual_output", {}).get("edge_case_flags", [])
        enhanced_flags.update(flags)
    
    all_flags = baseline_flags.union(enhanced_flags)
    
    for flag in sorted(all_flags):
        in_baseline = "✓" if flag in baseline_flags else "-"
        in_enhanced = "✓" if flag in enhanced_flags else "-"
        status = "Handled" if flag in enhanced_flags else "Not detected"
        report.append(f"| {flag} | {in_baseline} | {in_enhanced} | {status} |")
    
    report.append("")
    
    # Key Findings
    report.append("---")
    report.append("")
    report.append("## Key Findings")
    report.append("")
    
    report.append("### Strengths of Enhanced Implementation")
    report.append("")
    
    strengths = []
    
    if hierarchy_improvement['percent_change'] > 30:
        strengths.append("✅ **Information Hierarchy:** Core ticket information is properly emphasized and positioned at the top")
    
    if enhanced_metrics.get("scroll_length_reduction", 0) > 0.4:
        strengths.append("✅ **Scroll Reduction:** Collapsible sections significantly reduce page length")
    
    if misop_improvement['percent_change'] > 50:
        strengths.append("✅ **Mis-operation Prevention:** Clear visual distinctions between internal notes and customer replies")
    
    if enhanced_summary.get("edge_cases_covered", 0) > baseline_summary.get("edge_cases_covered", 0):
        strengths.append("✅ **Edge Case Handling:** Robust handling of malformed input, XSS attempts, and path traversal")
    
    if "xss_attempt_blocked" in enhanced_flags:
        strengths.append("✅ **Security:** HTML sanitization prevents XSS attacks")
    
    if "fullscreen_overlay_replaced" in enhanced_flags:
        strengths.append("✅ **Attachment Preview:** Non-blocking preview maintains context visibility")
    
    for strength in strengths:
        report.append(strength)
        report.append("")
    
    report.append("### Areas for Improvement")
    report.append("")
    
    # Check for unmet expectations across all scenarios
    all_unmet = set()
    for result in enhanced_results_list:
        behavior = result.get("validation_details", {}).get("behavior_validation", {})
        all_unmet.update(behavior.get("unmet_expectations", []))
    
    if all_unmet:
        for unmet in sorted(all_unmet)[:5]:
            report.append(f"⚠️ {unmet}")
            report.append("")
    else:
        report.append("✅ No significant areas for improvement identified.")
        report.append("")
    
    # Conclusion
    report.append("---")
    report.append("")
    report.append("## Conclusion")
    report.append("")
    
    overall_improvement = (
        hierarchy_improvement['percent_change'] +
        scroll_improvement['percent_change'] +
        misop_improvement['percent_change']
    ) / 3
    
    if overall_improvement > 100:
        conclusion = "**Outstanding improvement** achieved across all metrics."
    elif overall_improvement > 50:
        conclusion = "**Significant improvement** demonstrated in UI/UX optimization."
    elif overall_improvement > 25:
        conclusion = "**Moderate improvement** shown with room for further enhancement."
    else:
        conclusion = "**Limited improvement** - additional optimization recommended."
    
    report.append(conclusion)
    report.append("")
    report.append(f"The Enhanced Ticket UI (Project B) demonstrates **{overall_improvement:.1f}% average improvement** ")
    report.append("over the Baseline implementation across hierarchy clarity, scroll reduction, and mis-operation prevention.")
    report.append("")
    
    report.append("### Recommendations")
    report.append("")
    report.append("1. **Deploy Enhanced Implementation:** The improved UI/UX significantly reduces cognitive load and user errors")
    report.append("2. **Monitor User Feedback:** Track real-world usage to validate scroll reduction and interaction improvements")
    report.append("3. **Iterate on Edge Cases:** Continue refining malformed input handling and security measures")
    report.append("4. **Expand Collapsible Logic:** Consider adding more granular control for power users")
    report.append("")
    
    report.append("---")
    report.append("")
    report.append("*End of Report*")
    
    return "\n".join(report)


def main():
    """Generate comparison report."""
    print("Generating comparison report...")
    
    results_dir = Path("results")
    
    baseline_path = results_dir / "results_pre.json"
    enhanced_path = results_dir / "results_post.json"
    
    if not baseline_path.exists() or not enhanced_path.exists():
        print("Error: Results files not found!")
        print(f"  Looking for: {baseline_path}")
        print(f"  Looking for: {enhanced_path}")
        return
    
    baseline_results = load_results(str(baseline_path))
    enhanced_results = load_results(str(enhanced_path))
    
    if not baseline_results or not enhanced_results:
        print("Error: Could not load results!")
        return
    
    markdown_report = generate_markdown_report(baseline_results, enhanced_results)
    
    # Save report
    report_path = results_dir / "compare_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    print(f"Comparison report generated: {report_path}")
    print("")
    print("Summary:")
    print(f"  Baseline - Passed: {baseline_results.get('summary', {}).get('passed', 0)}/{baseline_results.get('summary', {}).get('total_scenarios', 0)}")
    print(f"  Enhanced - Passed: {enhanced_results.get('summary', {}).get('passed', 0)}/{enhanced_results.get('summary', {}).get('total_scenarios', 0)}")


if __name__ == "__main__":
    main()
