import json
import re

CORE_FIELDS = ["problem_description", "priority", "status"]


def detect_unsafe_html(s):
    if not isinstance(s, str):
        return False
    return bool(re.search(r"<\s*script|onerror=|onload=", s, flags=re.IGNORECASE))


class BaselineTransformer:
    """Baseline: minimal transformation, mostly pass-through, with simple detection."""

    def __init__(self, layout: dict):
        self.layout = layout or {}
        self.warnings = []
        self.errors = []
        self.metrics = {}

    def transform(self):
        out = {
            "title": self.layout.get("title"),
            "fields": self.layout.get("fields", []),
            "history": self.layout.get("history_entries", []),
            "meta": {
                "transform": "baseline",
            },
        }

        # Minimal checks
        # detect unsafe html
        for f in out.get("fields", []):
            if "content" in f and detect_unsafe_html(f.get("content")):
                self.warnings.append("unsafe_html_detected")
                self.errors.append("unsafe_html_detected")

        # compute naive hierarchy clarity: percentage of core fields in top 3
        fields = out.get("fields", [])
        top_labels = [f.get("label") for f in fields[:3]]
        found = sum(1 for c in CORE_FIELDS if c in top_labels)
        hierarchy_score = int((found / len(CORE_FIELDS)) * 100)
        self.metrics["hierarchy_clarity_score"] = hierarchy_score

        # mis-operation risk: if ambiguous action
        risk = 0
        for f in fields:
            if f.get("type") == "action" and f.get("meta", {}).get("scope") == "ambiguous":
                risk = 80
        self.metrics["mis_operation_risk"] = risk

        # fallback detection
        for f in fields:
            if f.get("type") not in ("primary", "secondary", "action", "notes", "container", "attachments"):
                self.warnings.append("unknown_field_type")
                self.errors.append("invalid_field_type")

        ret = {
            "status": "ok",
            "output_layout": out,
            "metrics": self.metrics,
            "ui_warnings": list(set(self.warnings)),
            "edge_case_flags": [],
            "errors": list(set(self.errors)),
        }

        return ret
