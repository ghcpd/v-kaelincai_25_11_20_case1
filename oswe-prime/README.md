# UI/UX Improvement Experiment - Ticket Detail Page

This workspace contains two projects:

- Project_A_BaselineTicketUI: a baseline pass-through transformer and naive metrics
- Project_B_EnhancedTicketUI: an enhanced transformer implementing UI/UX improvements

Shared assets in /shared include `test_scenarios.json` which describe the test cases.

Top-level scripts:
- `run_all.sh` - runs both projects tests and generates a compare report.

Run the tests with:

```bash
# On Linux/macOS
bash run_all.sh

# Or run each project individually
bash Project_A_BaselineTicketUI/run_tests.sh
bash Project_B_EnhancedTicketUI/run_tests.sh
```

On Windows (PowerShell):

```powershell
# Run both tests
bash ./run_all.sh
```

Results are saved under `results/` with `results_pre.json`, `results_post.json`, and `compare_report.md`.

Test Scenarios:
- normal_flow: overloaded layout with core info not prioritized — validates core_on_top, timeline collapse, non-blocking preview.
- mis_operation_flow: ambiguous reply vs internal note actions — validates internal differentiation, confirmation prompts.
- long_scroll_flow: long history — validates collapse and scroll reduction heuristics.
- complex_nesting: deep nested containers — validates flattening and re-grouping.
- malformed_input: missing fields/invalid types/unsafe HTML — validates safe fallback and robust error handling.

Metrics & Outputs:
- `hierarchy_clarity_score`: 0..100 score of core information at top.
- `mis_operation_risk`: heuristic 0..100 risk estimate of mis-operations.
- `collapsed_sections_count`: number of collapsed UI blocks.
- `ui_warnings`, `errors`: arrays of warnings/errors when malformed input or unsafe html is detected.

Limitations:
- This is a simulation: there is no real front-end. UI behaviors are modeled as JSON transforms and heuristics.
- The heuristics for metrics are simplified and intended to illustrate improvements rather than be exhaustive.
