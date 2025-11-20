# Project_B_EnhancedTicketUI

Enhanced transformer for the Ticket Detail Page. This project implements UI/UX improvements in a simulated transformation service.

How to run:

- Create Python venv and install deps: ./setup.sh
- Run tests + evaluation: ./run_tests.sh

Structure:
- src/transformer.py - enhanced transform logic
- src/evaluator.py - runs scenarios and writes results_post.json
- tests/test_transformer.py - unit tests against shared test_scenarios.json

Outputs (written to Project_B_EnhancedTicketUI/results):
- results_post.json - per-scenario results
- log_post.txt - simple logs
- summary_post.json - summary metrics
- enhanced_preview.html - small HTML mock artifact

Notes:
- This is a simulated backend-side transformation service. The UI artifacts are mock previews and not functional front-end code.
