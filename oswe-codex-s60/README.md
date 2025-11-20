# UI/UX Improvement Experiment — SaaS Ticket Detail Page

This workspace contains two projects:
- `Project_A_BaselineTicketUI` — baseline transformer (no UX improvements)
- `Project_B_EnhancedTicketUI` — enhanced transformer implementing UI/UX optimizations

Shared artifacts:
- `test_scenarios.json` — ≥5 scenarios covering normal, mis-operation, long-scroll, deep-nesting, malformed inputs
- `run_all.sh` / `run_all.ps1` — run both projects and aggregate results
- `results/` — aggregated comparison report (`compare_report.md`)

## Quick Start
```bash
bash run_all.sh
```
_On Windows, use Git Bash or run `run_all.ps1` in PowerShell (requires bash for project scripts)._ 

## Test Scenarios (Why They Matter)
1. **normal_overloaded_main_flow** — Validates hierarchy restructuring, collapsible history, non-blocking attachments.
2. **mis_operation_internal_external_confusion** — Ensures internal notes vs customer replies are visually distinct and critical actions prompt confirmation.
3. **long_scroll_history** — Confirms long histories are collapsed and scroll burden is reduced.
4. **complex_deep_nesting** — Tests reorganization of deeply nested layouts and flags depth issues.
5. **malformed_input_with_unsafe_html** — Validates safe fallback, sanitization, and robustness to invalid nodes.

## Outputs
- Project A: `Project_A_BaselineTicketUI/results/results_pre.json`, `logs/log_pre.txt`
- Project B: `Project_B_EnhancedTicketUI/results/results_post.json`, `logs/log_post.txt`
- Aggregate: `results/compare_report.md`, `results/combined_results.json`

## Metrics
- `hierarchy_clarity_score` — higher is better
- `scroll_length` — lower is better
- `misoperation_risk_score` — lower is better
- `attachment_usability_score` — 1.0 if no blocking overlays

## Limitations
- UI rendering is simulated (JSON layouts only)
- Metrics are heuristic
- Mis-operation risk evaluation uses simplified rules

## Common Pitfalls
- Not placing core info at the top
- Forgetting collapsible flags for history/logs
- Allowing attachment previews to block context
- Not sanitizing unsafe HTML
- Not differentiating internal vs customer-visible messages
