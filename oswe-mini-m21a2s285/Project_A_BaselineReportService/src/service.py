import time
import json

class BaselineReportService:
    """Simple, monolithic report service. No caching, synchronous export."""

    def __init__(self):
        # Simulated data store
        self.data = self._generate_data()

    def _generate_data(self):
        # Generate simple daily metrics
        return {"2025-11-19": {"views": 1000, "clicks": 120, "conversions": 15}}

    def get_report(self, date, dimensions=None, raw=False):
        # Sleep to simulate heavy computation
        time.sleep(1.2)  # heavy
        if date not in self.data:
            return {"status": "error", "error": "date_not_found"}
        metrics = self.data[date].copy()
        return {"status": "ok", "metrics": metrics, "pre_agg": False, "cache_hit": False}

    def export(self, date, columns=None):
        # Synchronous export - always heavy
        time.sleep(0.8)
        return {"status": "ok", "file": f"report_{date}.xlsx", "export_mode": "sync"}


if __name__ == '__main__':
    s = BaselineReportService()
    print(json.dumps(s.get_report('2025-11-19')))
