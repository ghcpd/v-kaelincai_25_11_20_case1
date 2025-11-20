# Project A – Baseline Ticket UI

This project simulates the overloaded, pre-improvement ticket detail page. It intentionally keeps the layout flat, renders history without collapse controls, and does not differentiate between internal notes and customer-facing replies. The goal is to provide a measurable **before** state.

## Structure
- `src/transformer.py` — baseline transformer that mostly passes layouts through.
- `tests/test_transformer.py` — loads shared scenarios, asserts baseline expectations, and writes `results_pre.json` plus `log_pre.txt`.
- `run_tests.sh` — bootstraps a virtual environment, runs the tests, and stores artifacts under `results/` and `logs/`.

## Environment Setup
```bash
./setup.sh
```
This script creates `.venv` and installs dependencies from `requirements.txt`.

## Running Tests
```bash
./run_tests.sh
```
The script sets the required environment variables, executes `pytest`, and leaves outputs in:
- `results/results_pre.json`
- `logs/log_pre.txt`

## Test Scenarios
All tests use `../test_scenarios.json`, which documents:
1. **Normal flow** – overloaded timeline with blocking attachments.
2. **Mis-operation flow** – identical note styles leading to risks.
3. **Long-scroll flow** – extremely long history causing scroll fatigue.
4. **Complex nesting** – deeply nested sections with no grouping.
5. **Malformed input** – invalid structures and unsafe HTML payloads.

Each scenario validates usability pitfalls such as missing hierarchy, lack of collapsible sections, unsafe fallbacks, and attachment previews that block the context. Baseline behavior is intentionally poor so that Project B can demonstrate measurable improvements.
