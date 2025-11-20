"""
Test harness for Project B - Enhanced Ticket UI
Loads test scenarios, validates transformations, and generates results.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ticket_ui_processor import process_ticket


class TestHarness:
    """Test harness for running and validating ticket UI transformations."""
    
    def __init__(self, test_scenarios_path: str):
        self.test_scenarios_path = test_scenarios_path
        self.results = []
        self.summary = {
            "total_scenarios": 0,
            "passed": 0,
            "failed": 0,
            "partial_success": 0,
            "edge_cases_covered": 0,
            "total_errors": 0,
            "total_warnings": 0
        }
    
    def load_scenarios(self) -> List[Dict[str, Any]]:
        """Load test scenarios from JSON file."""
        try:
            with open(self.test_scenarios_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("scenarios", [])
        except Exception as e:
            print(f"Error loading test scenarios: {e}")
            return []
    
    def run_tests(self) -> Dict[str, Any]:
        """Run all test scenarios."""
        print("=" * 80)
        print("ENHANCED TICKET UI - TEST EXECUTION")
        print("=" * 80)
        print()
        
        scenarios = self.load_scenarios()
        self.summary["total_scenarios"] = len(scenarios)
        
        for idx, scenario in enumerate(scenarios, 1):
            print(f"\n[{idx}/{len(scenarios)}] Running: {scenario['name']}")
            print(f"  ID: {scenario['id']}")
            print(f"  Description: {scenario['description']}")
            
            result = self.run_single_test(scenario)
            self.results.append(result)
            
            # Update summary
            status = result["test_status"]
            if status == "passed":
                self.summary["passed"] += 1
            elif status == "failed":
                self.summary["failed"] += 1
            elif status == "partial":
                self.summary["partial_success"] += 1
            
            self.summary["edge_cases_covered"] += len(result["actual_output"].get("edge_case_flags", []))
            self.summary["total_errors"] += len(result["actual_output"].get("errors", []))
            self.summary["total_warnings"] += len(result["actual_output"].get("ui_warnings", []))
            
            print(f"  Status: {status.upper()}")
            print(f"  Metrics: {result['actual_output']['metrics']}")
        
        return self.generate_report()
    
    def run_single_test(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test scenario."""
        scenario_id = scenario["id"]
        input_data = scenario["input"]
        expected_behavior = scenario.get("expected_behavior", {})
        expected_output = scenario.get("expected_output", {})
        
        # Process the ticket
        actual_output = process_ticket(input_data)
        
        # Validate results
        validation = self.validate_output(actual_output, expected_output, expected_behavior)
        
        return {
            "scenario_id": scenario_id,
            "scenario_name": scenario["name"],
            "test_status": validation["status"],
            "validation_details": validation,
            "actual_output": actual_output,
            "expected_output": expected_output
        }
    
    def validate_output(
        self, 
        actual: Dict[str, Any], 
        expected: Dict[str, Any],
        expected_behavior: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate actual output against expected output and behavior."""
        issues = []
        warnings = []
        
        # Check status
        expected_status = expected.get("status", "success")
        actual_status = actual.get("status", "unknown")
        
        # Check metrics - Enhanced version should meet or exceed expectations
        actual_metrics = actual.get("metrics", {})
        expected_metrics = expected.get("metrics", {})
        
        metrics_match = True
        metric_deltas = {}
        
        for key in ["hierarchy_clarity_score", "scroll_length_reduction", "mis_operation_risk"]:
            actual_val = actual_metrics.get(key, 0.0)
            expected_val = expected_metrics.get(key, 0.0)
            delta = abs(actual_val - expected_val)
            metric_deltas[key] = {
                "expected": expected_val,
                "actual": actual_val,
                "delta": round(delta, 2)
            }
            
            # Enhanced version should be close to expected good metrics
            tolerance = 0.2
            if delta > tolerance:
                metrics_match = False
                issues.append(f"{key}: expected ~{expected_val}, got {actual_val} (delta: {delta:.2f})")
        
        # Check expected behavior (enhanced should meet most)
        behavior_validation = self.validate_behavior(actual, expected_behavior)
        if not behavior_validation["all_met"]:
            warnings.extend(behavior_validation["unmet_expectations"])
            # For enhanced version, unmet expectations are more serious
            if len(behavior_validation["unmet_expectations"]) > 2:
                issues.append(f"Multiple behavioral expectations unmet: {len(behavior_validation['unmet_expectations'])}")
        
        # Determine test status
        if not issues and metrics_match and behavior_validation["all_met"]:
            status = "passed"
        elif actual_status == "partial_success" and not issues:
            status = "partial"
        else:
            status = "failed" if issues else "passed"
        
        return {
            "status": status,
            "issues": issues,
            "warnings": warnings,
            "metrics_comparison": metric_deltas,
            "behavior_validation": behavior_validation
        }
    
    def validate_behavior(
        self, 
        actual: Dict[str, Any], 
        expected_behavior: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that output meets expected behavioral requirements."""
        unmet = []
        met = []
        
        sections = actual.get("processed_sections", [])
        
        # Check hierarchy restructuring
        if expected_behavior.get("hierarchy_restructured"):
            core_at_top = [s for s in sections[:5] if s.get("type") in ["description", "priority", "status"]]
            if len(core_at_top) >= 2:
                met.append("hierarchy_restructured")
            else:
                unmet.append("hierarchy_not_restructured")
        
        # Check core info at top
        if expected_behavior.get("core_info_at_top"):
            expected_core = expected_behavior["core_info_at_top"]
            found_at_top = [s.get("type") for s in sections[:5]]
            core_found = sum(1 for t in expected_core if t in found_at_top)
            if core_found >= len(expected_core) - 1:  # Allow 1 missing
                met.append("core_info_at_top")
            else:
                unmet.append("core_info_not_at_top")
        
        # Check collapsible sections
        if expected_behavior.get("collapsible_sections"):
            expected_collapsible = expected_behavior["collapsible_sections"]
            for section_type in expected_collapsible:
                matching = [s for s in sections if s.get("type") == section_type]
                if matching and any(s.get("collapsible") for s in matching):
                    met.append(f"{section_type}_collapsible")
                else:
                    unmet.append(f"{section_type}_not_collapsible")
        
        # Check default collapsed
        if expected_behavior.get("default_collapsed"):
            expected_collapsed = expected_behavior["default_collapsed"]
            for section_type in expected_collapsed:
                matching = [s for s in sections if s.get("type") == section_type]
                if matching and any(s.get("collapsed") for s in matching):
                    met.append(f"{section_type}_collapsed_by_default")
                else:
                    unmet.append(f"{section_type}_not_collapsed_by_default")
        
        # Check attachment preview mode
        if expected_behavior.get("attachment_preview_non_blocking"):
            attachment_sections = [s for s in sections if s.get("type") == "attachments"]
            all_non_blocking = True
            for section in attachment_sections:
                files = section.get("files", [])
                for f in files:
                    if isinstance(f, dict):
                        mode = f.get("preview_mode", "unknown")
                        blocks = f.get("blocks_context", True)
                        if mode == "fullscreen_overlay" or blocks:
                            all_non_blocking = False
                            break
            if all_non_blocking and attachment_sections:
                met.append("attachment_preview_non_blocking")
            elif attachment_sections:
                unmet.append("attachment_preview_still_blocking")
        
        # Check communication distinction
        if expected_behavior.get("internal_notes_visually_distinct"):
            comm_sections = [s for s in sections if s.get("type") == "communication"]
            all_distinct = True
            for section in comm_sections:
                items = section.get("items", [])
                for item in items:
                    if isinstance(item, dict) and item.get("message_type") == "internal_note":
                        if item.get("visual_distinction") == "none":
                            all_distinct = False
                            break
            if all_distinct and comm_sections:
                met.append("internal_notes_visually_distinct")
            elif comm_sections:
                unmet.append("internal_notes_not_visually_distinct")
        
        if expected_behavior.get("customer_reply_visually_distinct"):
            comm_sections = [s for s in sections if s.get("type") == "communication"]
            all_distinct = True
            for section in comm_sections:
                items = section.get("items", [])
                for item in items:
                    if isinstance(item, dict) and item.get("message_type") == "customer_reply":
                        if item.get("visual_distinction") == "none":
                            all_distinct = False
                            break
            if all_distinct and comm_sections:
                met.append("customer_reply_visually_distinct")
            elif comm_sections:
                unmet.append("customer_reply_not_visually_distinct")
        
        # Check confirmation prompts
        if expected_behavior.get("confirmation_prompts"):
            expected_confirmations = expected_behavior["confirmation_prompts"]
            comm_sections = [s for s in sections if s.get("type") == "communication"]
            for section in comm_sections:
                items = section.get("items", [])
                for item in items:
                    if isinstance(item, dict):
                        msg_type = item.get("message_type", "")
                        if msg_type in expected_confirmations:
                            if item.get("confirmation_required"):
                                met.append(f"confirmation_for_{msg_type}")
                            else:
                                unmet.append(f"missing_confirmation_for_{msg_type}")
        
        # Check sanitization for malformed inputs
        if expected_behavior.get("sanitize_html"):
            if "xss_attempt_blocked" in actual.get("edge_case_flags", []):
                met.append("html_sanitized")
        
        if expected_behavior.get("prevent_path_traversal"):
            if "path_traversal_prevented" in actual.get("edge_case_flags", []):
                met.append("path_traversal_prevented")
        
        return {
            "all_met": len(unmet) == 0,
            "met_expectations": met,
            "unmet_expectations": unmet
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate final test report."""
        print("\n" + "=" * 80)
        print("TEST SUMMARY - ENHANCED TICKET UI")
        print("=" * 80)
        print(f"Total Scenarios: {self.summary['total_scenarios']}")
        print(f"Passed: {self.summary['passed']}")
        print(f"Failed: {self.summary['failed']}")
        print(f"Partial Success: {self.summary['partial_success']}")
        print(f"Edge Cases Covered: {self.summary['edge_cases_covered']}")
        print(f"Total Errors: {self.summary['total_errors']}")
        print(f"Total Warnings: {self.summary['total_warnings']}")
        print()
        
        # Calculate aggregate metrics
        avg_metrics = {
            "hierarchy_clarity_score": 0.0,
            "scroll_length_reduction": 0.0,
            "mis_operation_risk": 0.0
        }
        
        count = 0
        for result in self.results:
            metrics = result["actual_output"].get("metrics", {})
            for key in avg_metrics:
                avg_metrics[key] += metrics.get(key, 0.0)
                count = max(count, 1)
        
        for key in avg_metrics:
            avg_metrics[key] = round(avg_metrics[key] / len(self.results), 2) if self.results else 0.0
        
        print("Average Metrics:")
        print(f"  Hierarchy Clarity Score: {avg_metrics['hierarchy_clarity_score']}")
        print(f"  Scroll Length Reduction: {avg_metrics['scroll_length_reduction']}")
        print(f"  Mis-operation Risk: {avg_metrics['mis_operation_risk']}")
        print()
        
        return {
            "summary": self.summary,
            "average_metrics": avg_metrics,
            "results": self.results,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_results(self, output_dir: str):
        """Save test results to files."""
        os.makedirs(output_dir, exist_ok=True)
        
        report = self.generate_report()
        
        # Save JSON results
        results_file = os.path.join(output_dir, "results_post.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(f"Results saved to: {results_file}")
        
        # Save detailed log
        log_file = os.path.join(output_dir, "log_post.txt")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ENHANCED TICKET UI - DETAILED TEST LOG\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Test Run: {report['timestamp']}\n\n")
            
            for idx, result in enumerate(self.results, 1):
                f.write(f"\n{'=' * 80}\n")
                f.write(f"Test Case {idx}: {result['scenario_name']}\n")
                f.write(f"{'=' * 80}\n")
                f.write(f"Scenario ID: {result['scenario_id']}\n")
                f.write(f"Status: {result['test_status']}\n\n")
                
                f.write("Actual Metrics:\n")
                metrics = result['actual_output']['metrics']
                for key, value in metrics.items():
                    f.write(f"  {key}: {value}\n")
                
                f.write("\nValidation Issues:\n")
                issues = result['validation_details']['issues']
                if issues:
                    for issue in issues:
                        f.write(f"  - {issue}\n")
                else:
                    f.write("  None\n")
                
                f.write("\nBehavior Validation:\n")
                behavior = result['validation_details']['behavior_validation']
                f.write(f"  All Expectations Met: {behavior['all_met']}\n")
                if behavior['met_expectations']:
                    f.write("  Met Expectations:\n")
                    for met in behavior['met_expectations']:
                        f.write(f"    ✓ {met}\n")
                if behavior['unmet_expectations']:
                    f.write("  Unmet Expectations:\n")
                    for unmet in behavior['unmet_expectations']:
                        f.write(f"    ✗ {unmet}\n")
                
                f.write("\nWarnings:\n")
                warnings = result['actual_output'].get('ui_warnings', [])
                if warnings:
                    for warning in warnings:
                        f.write(f"  - {warning}\n")
                else:
                    f.write("  None\n")
                
                f.write("\nErrors:\n")
                errors = result['actual_output'].get('errors', [])
                if errors:
                    for error in errors:
                        f.write(f"  - {error}\n")
                else:
                    f.write("  None\n")
                
                f.write("\nEdge Case Flags:\n")
                flags = result['actual_output'].get('edge_case_flags', [])
                if flags:
                    for flag in flags:
                        f.write(f"  - {flag}\n")
                else:
                    f.write("  None\n")
                
                f.write("\n")
        
        print(f"Log saved to: {log_file}")


def main():
    """Main entry point for test execution."""
    # Determine paths
    script_dir = Path(__file__).parent.parent
    test_scenarios_path = script_dir.parent / "test_scenarios.json"
    results_dir = script_dir / "results"
    
    # Create and run test harness
    harness = TestHarness(str(test_scenarios_path))
    harness.run_tests()
    harness.save_results(str(results_dir))
    
    print("\n" + "=" * 80)
    print("TEST EXECUTION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
