import re
from copy import deepcopy
from typing import List

CORE_FIELDS = ["problem_description", "priority", "status"]


def detect_unsafe_html(s):
    if not isinstance(s, str):
        return False
    return bool(re.search(r"<\s*script|onerror=|onload=", s, flags=re.IGNORECASE))


class EnhancedTransformer:
    """Enhanced transformer implementing UI/UX improvements.

    Key behaviors:
    - Ensure core fields are highlighted and placed at the top
    - Default collapse of history/logs and related sections
    - Convert blocking attachment preview into 'side-panel' preview
    - Differentiate internal notes vs customer-visible replies
    - Confirmation prompts for critical actions
    - Safe fallback for malformed inputs or unsafe HTML
    - Flatten deeply nested container structures
    """

    def __init__(self, layout: dict):
        self.src = deepcopy(layout) or {}
        self.warnings = []
        self.errors = []
        self.metrics = {}

    def flatten_fields(self, fields: List[dict]):
        flat = []
        for f in fields:
            if f.get("type") == "container" and "children" in f:
                # recursively flatten
                flat.extend(self.flatten_fields(f.get("children", [])))
            else:
                flat.append(f)
        return flat

    def highlight_field(self, field):
        f = deepcopy(field)
        f["ui"] = f.get("ui", {})
        f["ui"]["highlight"] = True
        return f

    def collapse_field(self, field):
        f = deepcopy(field)
        # default collapsed for timeline/logs/related
        f["ui"] = f.get("ui", {})
        f["ui"]["collapsed"] = True
        return f

    def safe_content(self, content):
        if detect_unsafe_html(content):
            self.warnings.append("unsafe_html_detected")
            self.errors.append("unsafe_html_detected")
            return "[removed unsafe content]"
        return content

    def transform(self):
        fields = self.src.get("fields", [])
        flat = self.flatten_fields(fields)

        # sanitize
        for f in flat:
            if "content" in f and isinstance(f.get("content"), str):
                f["content"] = self.safe_content(f.get("content"))
            # invalid types
            if f.get("type") not in ("primary", "secondary", "action", "notes", "container", "attachments", "unknown"):
                self.errors.append("invalid_field_type")

        # ensure core fields are present; bring to top if found
        core_found = []
        remaining = []
        for f in flat:
            if f.get("label") in CORE_FIELDS:
                core_found.append(self.highlight_field(f))
            else:
                remaining.append(f)

        # If missing core fields, add placeholders as errors
        for c in CORE_FIELDS:
            if c not in [f.get("label") for f in core_found]:
                self.warnings.append(f"missing_core_field_{c}")
                self.errors.append(f"missing_core_field_{c}")

        # collapse timeline/logs and related tickets
        processed = []
        for f in remaining:
            # attachments must be transformed to non-blocking preview regardless of type
            if f.get("type") == "attachments" or f.get("label") == "attachments":
                g = deepcopy(f)
                g["ui"] = g.get("ui", {})
                g["ui"]["preview_mode"] = "side-panel"
                # attachments are also collapsed by default (less intrusive)
                g["ui"]["collapsed"] = True
                processed.append(g)
                continue
            if f.get("label") in ("history", "historical_log", "logs", "related_tickets") or f.get("type") == "secondary":
                processed.append(self.collapse_field(f))
            elif f.get("type") == "attachments" or f.get("label") == "attachments":
                g = deepcopy(f)
                g["ui"] = g.get("ui", {})
                # non-blocking preview by default
                g["ui"]["preview_mode"] = "side-panel"
                processed.append(g)
            elif f.get("type") == "notes":
                g = deepcopy(f)
                g["ui"] = g.get("ui", {})
                # clear differentiation for internal notes
                g["ui"]["internal"] = True
                processed.append(g)
            elif f.get("type") == "action":
                g = deepcopy(f)
                g["ui"] = g.get("ui", {})
                if f.get("meta", {}).get("scope") == "ambiguous":
                    # force confirmation to reduce mis-operation
                    g["ui"]["require_confirmation"] = True
                    g["ui"]["confirm_message"] = "This action may be customer-visible. Confirm?"
                processed.append(g)
            else:
                processed.append(f)

        # Recompose layout with core fields at top
        out_fields = core_found + processed

        out = {
            "title": self.src.get("title"),
            "fields": out_fields,
            "history": self.src.get("history_entries", []),
            "meta": {
                "transform": "enhanced",
            },
        }

        # metrics
        # hierarchy clarity: count of highlighted core fields in top 3
        top_labels = [f.get("label") for f in out_fields[:3]]
        found = sum(1 for c in CORE_FIELDS if c in top_labels)
        hierarchy_score = int((found / len(CORE_FIELDS)) * 100)

        self.metrics["hierarchy_clarity_score"] = hierarchy_score

        # mis-operation risk reduced
        risk = 20
        # find any action without confirmation
        for f in out_fields:
            if f.get("type") == "action":
                if not f.get("ui", {}).get("require_confirmation"):
                    # still risky
                    risk += 30
        self.metrics["mis_operation_risk"] = min(risk, 100)

        # history collapsed percentage - if we collapsed history entries
        collapsed_count = sum(1 for f in out_fields if f.get("ui", {}).get("collapsed"))
        self.metrics["collapsed_sections_count"] = collapsed_count

        ret = {
            "status": "ok",
            "output_layout": out,
            "metrics": self.metrics,
            "ui_warnings": list(set(self.warnings)),
            "edge_case_flags": [],
            "errors": list(set(self.errors)),
        }
        return ret
