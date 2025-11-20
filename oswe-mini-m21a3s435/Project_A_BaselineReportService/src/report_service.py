import time
import json
from typing import Dict, Any


class BaselineReportService:
    """Monolithic reporting service: single heavy endpoint, synchronous exports."""

    def __init__(self):
        # Simulated raw data
        self._data = self._generate_data()

    def _generate_data(self):
        # produce a simple dataset of daily metrics by region/channel/campaign
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

    def get_report(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request synchronously (no layered loading).

        Supports keys: granularity, dimensions (dict), export (bool)
        """
        # simulate heavy processing
        time.sleep(1.2)

        granularity = request.get("granularity", "day")
        dims = request.get("dimensions", {})

        if granularity not in ("day", "week", "month"):
            return {"status": "error", "errors": ["invalid granularity"]}

        # filter
        filtered = self._data
        for k, v in dims.items():
            if not isinstance(v, str):
                return {"status": "error", "errors": ["dimension must be string"]}
            filtered = [r for r in filtered if r.get(k) == v]

        # aggregate naive
        metrics = {"impressions": 0, "clicks": 0, "revenue": 0.0}
        for r in filtered:
            metrics["impressions"] += r["impressions"]
            metrics["clicks"] += r["clicks"]
            metrics["revenue"] += r["revenue"]

        output = {"status": "ok", "metrics": metrics, "cache_hit": False}

        if request.get("export"):
            # synchronous export
            path = request.get("export_path", "results/export_full.xlsx")
            # we just write a JSON file as a placeholder
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(output, fh)
            output["exported"] = path

        return output
