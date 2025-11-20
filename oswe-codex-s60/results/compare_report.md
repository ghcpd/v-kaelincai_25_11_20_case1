# Comparison Report

## Pass/Fail Matrix
| Scenario | Baseline Status | Enhanced Status | Δ Clarity | Δ Scroll | Δ Mis-op Risk |
|----------|-----------------|-----------------|----------:|---------:|--------------:|
| complex_deep_nesting | pass | pass | +0.950 | +1.500 | -0.100 |
| long_scroll_history | pass | pass | +0.000 | +50.500 | -0.100 |
| malformed_input_with_unsafe_html | pass | pass | +0.489 | -0.000 | -0.100 |
| mis_operation_internal_external_confusion | pass | pass | +0.000 | -0.000 | +0.600 |
| normal_overloaded_main_flow | pass | pass | +0.700 | +2.500 | -0.100 |

## Averages
- Baseline clarity: 0.1622
- Enhanced clarity: 0.59
- Baseline scroll length: 11.2
- Enhanced scroll length: 0.3
- Baseline mis-op risk: 0.32
- Enhanced mis-op risk: 0.27999999999999997

## Highlights
- Hierarchy clarity delta should be positive (higher is better)
- Scroll length delta should be negative (lower is better)
- Mis-operation risk delta should be negative (lower is better)