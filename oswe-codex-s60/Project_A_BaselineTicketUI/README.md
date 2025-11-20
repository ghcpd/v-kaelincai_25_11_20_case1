# Project A – Baseline Ticket UI

A simplistic baseline transformation for the SaaS Ticket Detail Page. It **does not** implement UI/UX improvements (no hierarchy restructuring, no collapsible sections, no attachment-preview optimization, no mis-operation prevention). It mainly ensures data passes through without crashing and computes naive metrics.

## Structure
- `src/`
  - `transformer.py` — baseline transformer
  - `metrics.py` — naive metric computation
  - `utils.py` — helpers (repeat expansion, sanitization)
  - `generate_results.py` — produce `results_pre.json` and `log_pre.txt`
- `tests/` — pytest suite validating the baseline behavior
- `logs/`, `results/` — output directories
- `requirements.txt`, `setup.sh`, `run_tests.sh`

## Setup
```bash
bash setup.sh
```

## Run Tests & Generate Results
```bash
bash run_tests.sh
```
Outputs:
- `results/results_pre.json`
- `logs/log_pre.txt`

## Notes
- This baseline intentionally leaves UI/UX issues unaddressed to provide a before/after comparison with Project B.
- Metrics are heuristic and simplified; improvements are expected in Project B.
