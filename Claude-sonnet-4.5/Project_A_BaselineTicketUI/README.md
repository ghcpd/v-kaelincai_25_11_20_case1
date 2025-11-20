# Project A - Baseline Ticket UI

## Overview

This is the **baseline implementation** representing the current state of a SaaS Ticket Detail Page with poor UI/UX design. This implementation serves as the "before" state for comparison against the enhanced version.

## Problems with Baseline Implementation

The baseline implementation suffers from:

1. **No Information Hierarchy**: Critical fields (problem description, priority, status) are not emphasized or prioritized
2. **No Collapsible Sections**: History, logs, and related tickets are always fully expanded, causing excessive scrolling
3. **Blocking Attachment Preview**: Fullscreen overlays block access to ticket information
4. **No Visual Distinctions**: Internal notes and customer-visible replies look identical, causing mis-operations
5. **No Confirmation Prompts**: Critical actions have no safety checks
6. **Flat Visual Structure**: Uniform fonts, colors, and spacing reduce scannability

## Project Structure

```
Project_A_BaselineTicketUI/
├── src/
│   └── ticket_ui_processor.py    # Baseline processor implementation
├── tests/
│   └── test_runner.py             # Test harness
├── results/                       # Test results (generated)
├── logs/                          # Test logs (generated)
├── requirements.txt               # Python dependencies
├── setup.sh                       # Setup script (Linux/Mac)
├── run_tests.sh                   # Test runner (Linux/Mac)
├── run_tests.ps1                  # Test runner (Windows)
└── README.md                      # This file
```

## Setup

### Prerequisites
- Python 3.7 or higher

### Installation

**Linux/Mac:**
```bash
bash setup.sh
```

**Windows:**
No setup required - uses system Python.

## Running Tests

### Linux/Mac
```bash
bash run_tests.sh
```

### Windows (PowerShell)
```powershell
.\run_tests.ps1
```

### Manual Execution
```bash
python tests/test_runner.py
```

## Test Scenarios

The test harness loads scenarios from `../test_scenarios.json` covering:

1. **Normal Overloaded Ticket**: Standard ticket with excessive scrolling and buried key info
2. **Mis-operation Risk**: Internal notes vs customer replies confusion
3. **Extreme Scroll**: 100+ history entries causing excessive scrolling
4. **Deep Nesting**: Complex nested layout requiring intelligent grouping
5. **Malformed Input**: Missing fields, type mismatches, XSS attempts
6. **Attachment Blocking**: Fullscreen previews blocking context

## Expected Results

The baseline implementation is **intentionally poor** and will demonstrate:

- ❌ **Low hierarchy clarity score** (~0.3-0.4): No prioritization of core info
- ❌ **Zero scroll reduction** (0.0): Nothing is collapsed
- ❌ **High mis-operation risk** (~0.5-0.9): No visual distinctions
- ❌ **Poor edge case handling**: Minimal sanitization or validation

## Output Files

After running tests:

- `results/results_pre.json`: Detailed test results in JSON format
- `results/log_pre.txt`: Human-readable test log
- Test status, metrics, warnings, and errors for each scenario

## Key Metrics

### Hierarchy Clarity Score (0.0 - 1.0)
- Measures how well core information is emphasized
- **Baseline Expected**: 0.3 - 0.4 (poor)

### Scroll Length Reduction (0.0 - 1.0)
- Measures reduction in page scroll through collapsing
- **Baseline Expected**: 0.0 (no reduction)

### Mis-operation Risk (0.0 - 1.0, lower is better)
- Measures risk of user errors
- **Baseline Expected**: 0.5 - 0.9 (high risk)

## Common Issues in Baseline

1. **Core information buried**: Priority and status appear after history
2. **No section collapsing**: Long history always fully expanded
3. **Fullscreen attachments**: Preview blocks ticket information
4. **Identical communication styles**: Can't distinguish internal vs customer messages
5. **No safety checks**: No confirmation prompts for critical actions

## Limitations

This is a **simulated UI processor**, not actual front-end rendering:
- UI transformations are modeled as data structures
- Layout metrics are computed algorithmically
- No actual HTML/CSS rendering occurs
- Focus is on structural and behavioral correctness

## Next Steps

After reviewing baseline results, compare with **Project_B_EnhancedTicketUI** to see UI/UX improvements.

## License

This is evaluation code for AI model testing purposes.
