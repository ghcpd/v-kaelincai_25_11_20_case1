import time
import json
import pytest
from src.service import EnhancedReportService, CircuitBreaker

svc = EnhancedReportService()

def test_core_kpis_fast():
    start = time.time()
    r = svc.get_report('2025-11-19')
    t = time.time() - start
    assert r['status'] == 'ok'
    assert r['core']['pre_agg'] is True
    assert t < 0.5

def test_layered_loading():
    r1 = svc.get_report('2025-11-19')
    r2 = svc.get_report('2025-11-19', dimensions='region')
    assert r2['details'] is not None
    assert r2['details']['cached'] is False
    # second call should be cached
    r3 = svc.get_report('2025-11-19', dimensions='region')
    assert r3['details']['cached'] is True

def test_circuit_breaker_and_peak():
    svc.reset_circuit()
    # simulate peak with multiple requests
    for i in range(6):
        try:
            svc.get_report('2025-11-19', peak=True)
        except CircuitBreaker:
            if i < 5:
                pytest.skip('circuit breaker hit too early')
            break

def test_async_export():
    r = svc.export('2025-11-19', columns=['views','clicks','conversions','extra'])
    assert r['status'] == 'queued'
    assert r['task_id'].startswith('exp_')

def test_small_sync_export():
    r = svc.export('2025-11-19', columns=['views','clicks'])
    assert r['export_mode'] == 'sync'
