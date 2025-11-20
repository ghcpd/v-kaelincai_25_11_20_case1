import time
import json
import threading
import queue

class CircuitBreaker(Exception):
    pass

class EnhancedReportService:
    def __init__(self):
        self.raw_store = {"2025-11-19": {"views": 1000, "clicks": 120, "conversions": 15}}
        # Pre-aggregated store simulating OLAP
        self.pre_agg = {"daily": {"2025-11-19": {"views": 1000, "clicks": 120}}}
        self.cache = {}
        self.last_sync = {"daily": "2025-11-19T03:00:00Z", "incremental_done": True}
        self.lock = threading.Lock()
        self.request_cost = 0
        self.circuit_open = False
        # Async export
        self.export_queue = queue.Queue()
        t = threading.Thread(target=self._export_worker, daemon=True)
        t.start()

    def _export_worker(self):
        while True:
            task = self.export_queue.get()
            if task is None:
                break
            time.sleep(0.5)  # simulate background work
            task['result'] = {"status": "ready", "file": f"{task['id']}.xlsx"}
            self.export_queue.task_done()

    def get_core_kpis(self, date):
        # Fast core KPI path using pre-agg
        time.sleep(0.1)
        if date in self.pre_agg['daily']:
            return {"status": "ok", "metrics": self.pre_agg['daily'][date], "pre_agg": True, "cache_hit": True}
        return {"status": "ok", "metrics": self.raw_store.get(date, {}), "pre_agg": False, "cache_hit": False}

    def get_dimensions(self, date, dimension):
        # Deferred heavy dimension load
        time.sleep(0.3)
        key = f"{date}:{dimension}"
        if key in self.cache:
            return {"status": "ok", "metrics": self.cache[key], "cached": True}
        # simulate heavy aggregation
        res = {dimension: {"A": 10, "B": 20}}
        self.cache[key] = res
        return {"status": "ok", "metrics": res, "cached": False}

    def get_report(self, date, dimensions=None, peak=False):
        if self.circuit_open:
            raise CircuitBreaker('Service overloaded')
        with self.lock:
            self.request_cost += 1
            if peak and self.request_cost > 5:
                # trip circuit
                self.circuit_open = True
                raise CircuitBreaker('Rate limit exceeded')
        core = self.get_core_kpis(date)
        details = None
        if dimensions:
            details = self.get_dimensions(date, dimensions)
        return {"status": "ok", "core": core, "details": details, "freshness": self.last_sync, "in_progress": not self.last_sync.get('incremental_done', False)}

    def export(self, date, columns=None):
        # small exports handled synchronously if <3 columns
        if columns and len(columns) < 3:
            time.sleep(0.2)
            return {"status": "ok", "file": f"report_{date}_small.xlsx", "export_mode": "sync"}
        # otherwise queue async
        task = {"id": f"exp_{int(time.time()*1000)}", "date": date}
        self.export_queue.put(task)
        return {"status": "queued", "task_id": task['id']}

    def reset_circuit(self):
        self.circuit_open = False
        self.request_cost = 0

if __name__ == '__main__':
    svc = EnhancedReportService()
    print(json.dumps(svc.get_report('2025-11-19')))
