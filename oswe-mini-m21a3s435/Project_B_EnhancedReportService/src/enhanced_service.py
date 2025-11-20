import time
import json
from functools import lru_cache
from threading import Thread, Lock
from queue import Queue
from typing import Dict, Any, Tuple


class CircuitBreaker(Exception):
    pass


class EnhancedReportService:
    def __init__(self):
        self._data = self._generate_data()
        self._olap = self._build_preagg()
        self._freshness = {"last_full_sync": time.time() - 60 * 60 * 24, "incremental_in_progress": False}

        # concurrency control
        self._lock = Lock()
        self._active_cost = 0
        self._cost_threshold = 30  # arbitrary

        # async export queue
        self._export_queue = Queue()
        self._export_worker = Thread(target=self._export_worker_loop, daemon=True)
        self._export_worker.start()

    def _generate_data(self):
        data = []
        for day in range(1, 31):
            for region in ["NA", "EMEA", "APAC"]:
                for channel in ["email", "web", "ads"]:
                    for campaign in ["A", "B", "C"]:
                        data.append({
                            "day": f"2025-11-{day:02}",
                            "region": region,
                            "channel": channel,
                            "campaign": campaign,
                            "impressions": 1000 + day,
                            "clicks": 50 + day % 7,
                            "revenue": 100.0 + day * 0.5,
                        })
        return data

    def _build_preagg(self):
        # build pre-aggregated totals by day/region/channel
        olap = {}
        for r in self._data:
            key = (r["day"], r["region"], r["channel"])
            if key not in olap:
                olap[key] = {"impressions": 0, "clicks": 0, "revenue": 0.0}
            olap[key]["impressions"] += r["impressions"]
            olap[key]["clicks"] += r["clicks"]
            olap[key]["revenue"] += r["revenue"]
        return olap

    def _export_worker_loop(self):
        while True:
            task = self._export_queue.get()
            if task is None:
                break
            job_id, payload, out_path = task
            time.sleep(0.6)  # simulate work
            with open(out_path, "w", encoding="utf-8") as fh:
                json.dump({"job_id": job_id, "payload": payload}, fh)

    def get_freshness(self) -> Dict[str, Any]:
        # Simulate incremental tracking
        now = time.time()
        last = self._freshness["last_full_sync"]
        lag = (now - last) / 3600.0
        return {"last_full_sync_hours_ago": lag, "incremental_in_progress": self._freshness["incremental_in_progress"]}

    def _acquire_cost(self, cost: int) -> None:
        with self._lock:
            if self._active_cost + cost > self._cost_threshold:
                raise CircuitBreaker("cost threshold exceeded")
            self._active_cost += cost

    def _release_cost(self, cost: int) -> None:
        with self._lock:
            self._active_cost = max(0, self._active_cost - cost)

    def get_core_kpis(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # cheap, returns overall sums quickly
        # small sleep to simulate quick load
        time.sleep(0.08)
        total = {"impressions": 0, "clicks": 0, "revenue": 0.0}
        for r in self._data:
            total["impressions"] += r["impressions"]
            total["clicks"] += r["clicks"]
            total["revenue"] += r["revenue"]

        return {"status": "ok", "metrics": total, "cache_hit": False}

    @lru_cache(maxsize=128)
    def get_dimensions(self, granularity: str, dim_key: Tuple[str, str]) -> Dict[str, Any]:
        # more expensive
        time.sleep(0.25)
        # dim_key example: ("region","NA")
        keyset = [k for k in self._data if k.get(dim_key[0]) == dim_key[1]]
        metrics = {"impressions": 0, "clicks": 0, "revenue": 0.0}
        for r in keyset:
            metrics["impressions"] += r["impressions"]
            metrics["clicks"] += r["clicks"]
            metrics["revenue"] += r["revenue"]
        return {"status": "ok", "metrics": metrics, "cache_hit": True}

    def query(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # cost calculation
        cost = 5 if request.get("dimensions") else 2
        try:
            self._acquire_cost(cost)
        except CircuitBreaker:
            return {"status": "fallback", "error": "cost_threshold_exceeded", "circuit": True}

        try:
            gran = request.get("granularity", "day")
            dims = request.get("dimensions", {})

            # if supported in preagg, fetch from olap
            if gran == "day" and len(dims) == 2 and tuple(dims.items())[0] and tuple(dims.items())[1]:
                # try preagg
                try:
                    # pick a key we support (day, region, channel)
                    if set(dims.keys()) >= set(["day", "region"]):
                        key = (dims["day"], dims.get("region"), dims.get("channel", "web"))
                        val = self._olap.get(key)
                        if val:
                            return {"status": "ok", "metrics": val, "preagg": True, "cache_hit": False}
                except Exception:
                    pass

            # fallback: layered loading - return core quick then allow dimensions
            core = self.get_core_kpis(request)

            # if the client asks for dimension details, fetch separately
            if dims:
                # pick first dim
                k, v = next(iter(dims.items()))
                dim_detail = self.get_dimensions(gran, (k, v))
                core["dimensions"] = dim_detail

            # add freshness
            core["freshness"] = self.get_freshness()

            return core
        finally:
            self._release_cost(cost)

    def export(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # small exports synchronous; large exports queued
        rows_estimate = 1000
        if request.get("dimensions"):
            rows_estimate = 100

        if rows_estimate > 500:
            # async job
            job_id = f"job_{int(time.time()*1000)}"
            out_path = request.get("export_path", f"results/{job_id}.json")
            self._export_queue.put((job_id, {"req": request}, out_path))
            return {"status": "accepted", "job_id": job_id}
        else:
            # synchronous
            time.sleep(0.15)
            out_path = request.get("export_path", "results/export_small.json")
            with open(out_path, "w", encoding="utf-8") as fh:
                json.dump({"req": request}, fh)
            return {"status": "ok", "exported": out_path}
