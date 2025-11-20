# Project_B_EnhancedTicketUI

Enhanced transformer and tests.

Setup:

```bash
# On Linux/macOS
cd Project_B_EnhancedTicketUI
bash setup.sh
bash run_tests.sh

# On Windows PowerShell
python -m venv .env
.\.env\Scripts\activate
pip install -r requirements.txt
pytest -q
```

Results are written to `results/results_post.json` and `results/log_post.txt`.

Key behavior validated in tests:
- `core_on_top` and hierarchy clarity metrics for core information
- `timeline_collapsed` and collapsed sections behavior
- `preview_blocking` false for attachments preview
- `internal_clear` separation for notes and confirmation prompts for ambiguous actions
- `safe_fallback` detection and error handling for malformed inputs

To run an end-to-end comparison locally, from workspace root run:

```bash
bash run_all.sh
```
