# Project B – Enhanced Ticket UI

This project implements the improved ticket detail experience described in the evaluation brief. It performs dynamic restructuring, collapses overloaded timelines, differentiates note channels, sanitizes unsafe payloads, and enforces confirmation prompts for risky interactions.

## Structure
- `src/transformer.py` — enhancement engine that reorganizes layouts, adds safeguards, and produces evaluation metrics.
- `tests/test_transformer.py` — scenario-driven regression suite validating collapsible behavior, attachment preview changes, and fallback logic for malformed layouts.
- `run_tests.sh` — prepares the Python environment, runs all tests, and saves artifacts to `results/` and `logs/`.

## Environment Setup
```bash
./setup.sh
```
Creates `.venv` and installs dependencies.

## Running Tests
```bash
./run_tests.sh
```
Outputs:
- `results/results_post.json`
- `logs/log_post.txt`

## Scenario Coverage
The reuse of `../test_scenarios.json` ensures both projects are evaluated against identical inputs:
1. **Normal flow** – verifies core information is promoted, timelines collapsed, and attachments rendered via side panel.
2. **Mis-operation flow** – enforces channel-specific styling and confirmation prompts.
3. **Long-scroll flow** – collapses extremely long histories and records scroll savings.
4. **Complex nesting** – flattens nested containers, re-groups related sections, and keeps history collapsed.
5. **Malformed input** – tests sanitization of unsafe HTML, type coercion, and graceful degradation.

Each scenario yields measurable deltas in clarity, collapsibility, and risk reduction which are later compared in `compare_report.md`.
