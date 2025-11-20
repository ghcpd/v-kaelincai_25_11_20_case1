import time
import json
from src.service import BaselineReportService

service = BaselineReportService()

def test_daily_report():
    start = time.time()
    r = service.get_report('2025-11-19')
    elapsed = time.time() - start
    assert r['status'] == 'ok'
    assert 'views' in r['metrics']
    # baseline should be relatively slow
    assert elapsed >= 1.0

def test_export_sync():
    r = service.export('2025-11-19')
    assert r['export_mode'] == 'sync'

def test_missing_date():
    r = service.get_report('2025-11-01')
    assert r['status'] == 'error'
