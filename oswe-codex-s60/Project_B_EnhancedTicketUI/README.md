# Project B – Enhanced Ticket UI

A robust UI/UX transformation for the SaaS Ticket Detail Page implementing:
- **Information hierarchy restructuring** (core info block at top)
- **Collapsible sections** for history/logs/related tickets (default collapsed)
- **Attachment preview optimization** (non-blocking side-panel)
- **Internal vs. external differentiation** with visual tags
- **Confirmation prompts** for critical actions
- **Safe fallback** for malformed layouts and unsafe HTML

## Structure
- `src/`
  - `transformer.py` — enhanced transformer
  - `metrics.py` — improvement-focused metrics
  - `utils.py` — helpers (repeat expansion, sanitization)
  - `generate_results.py` — produce `results_post.json` and `log_post.txt`
- `tests/` — pytest suite validating enhanced behaviors
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
- `results/results_post.json`
- `logs/log_post.txt`

## Notes
- Metrics are heuristic but demonstrate improvement over the baseline.
- Transformation is resilient to malformed inputs and deeply nested layouts.
