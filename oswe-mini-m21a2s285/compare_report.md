# Comparison Report

This report summarizes baseline vs enhanced behavior on synthetic scenarios.

- Latency: Enhanced shows faster core KPI path (pre-aggregated) and deferred dimension loading. See results/report comparisons.
- Freshness: Enhanced exposes last_sync metadata and in_progress flag for early morning partials.
- Concurrency: Enhanced implements rudimentary circuit breaker to prevent overload in peak.
- Exports: Baseline synchronous only; Enhanced uses sync for small exports and async queue for large exports.
- UI: Enhanced Ticket UI prioritizes core info, collapses history, and uses side-panel attachment preview.

Run shared/run_all.sh to generate detailed JSON results and logs in results/.
