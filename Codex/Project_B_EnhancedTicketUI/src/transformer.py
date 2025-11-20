"""
Enhanced ticket layout transformer that applies the requested UI/UX improvements.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Tuple

CORE_FIELDS = ("problem_description", "priority", "status")
TIMELINE_CATEGORIES = {"history", "logs", "related"}


class TicketLayoutTransformer:
    """Full-featured transformer for the improved ticket page."""

    def transform(self, layout_def: Any) -> Dict[str, Any]:
        layout_copy = deepcopy(layout_def) if isinstance(layout_def, dict) else {}
        normalized, warnings, flags = self._normalize(layout_copy)
        restructured, restructure_flags = self._restructure(normalized)
        flags.extend(flag for flag in restructure_flags if flag not in flags)
        metrics = self._compute_metrics(restructured, flags)
        return {
            "status": "success",
            "metrics": metrics,
            "ui_warnings": warnings,
            "edge_case_flags": flags,
            "errors": [],
            "layout": restructured,
        }

    def _normalize(self, layout: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str], List[str]]:
        warnings: List[str] = []
        flags: List[str] = []

        sections = layout.get("sections", [])
        if not isinstance(sections, list):
            warnings.append("sections-rebuilt")
            self._add_flag(flags, "malformed-corrected")
            sections = []
        normalized_sections, depth = self._flatten_sections(sections)
        if depth > 2:
            flags.append("nesting-regrouped")

        notes = layout.get("notes", [])
        if not isinstance(notes, list):
            warnings.append("notes-rebuilt")
            self._add_flag(flags, "malformed-corrected")
            notes = []

        attachments = layout.get("attachments", {})
        if not isinstance(attachments, dict):
            attachments = {}
        if attachments.get("unsafe_payload"):
            attachments.pop("unsafe_payload", None)
            warnings.append("sanitized-html")
            self._add_flag(flags, "html-neutralized")

        actions = layout.get("actions", [])
        if not isinstance(actions, list):
            self._add_flag(flags, "malformed-corrected")
            actions = []

        normalized = {
            "sections": normalized_sections,
            "notes": notes,
            "attachments": attachments or {"mode": "inline", "items": []},
            "actions": actions,
            "meta": layout.get("meta", {}),
        }
        return normalized, warnings, flags

    def _restructure(self, layout: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        flags: List[str] = []
        sections = layout["sections"]
        core_section = self._build_core_section(sections, layout.get("meta", {}))

        supporting_sections: List[Dict[str, Any]] = []
        timeline_sections: List[Dict[str, Any]] = []
        for section in sections:
            if self._is_core_section(section):
                continue
            if section.get("category") in TIMELINE_CATEGORIES:
                section["collapsed"] = True
                section["summary_count"] = len(section.get("items", []))
                timeline_sections.append(section)
            else:
                supporting_sections.append(section)
        supporting_sections.sort(key=lambda sec: sec.get("title") or "")
        reorganized_sections = [core_section] + supporting_sections + timeline_sections
        layout["sections"] = reorganized_sections

        history_length = sum(
            len(section.get("items", []))
            for section in timeline_sections
            if section.get("category") in TIMELINE_CATEGORIES
        )
        if history_length > 20:
            flags.append("long-history-collapsed")

        layout["attachments"] = self._modernize_attachments(layout["attachments"])
        note_flags = self._differentiate_notes(layout["notes"])
        flags.extend(flag for flag in note_flags if flag not in flags)
        layout["actions"] = self._enforce_confirmations(layout["actions"])

        return layout, flags

    def _build_core_section(self, sections: List[Dict[str, Any]], meta: Dict[str, Any]) -> Dict[str, Any]:
        core_values = {field: meta.get(field) for field in CORE_FIELDS}
        for section in sections:
            if not self._is_core_section(section):
                continue
            for item in section.get("items", []):
                field_name = item.get("field")
                if field_name in CORE_FIELDS:
                    core_values[field_name] = item.get("value")
        items = [
            {"field": field, "value": core_values.get(field), "emphasis": True}
            for field in CORE_FIELDS
        ]
        return {
            "id": "core-information",
            "title": "Core Ticket Overview",
            "category": "core",
            "collapsed": False,
            "items": items,
            "children": [],
            "highlight": True,
        }

    def _modernize_attachments(self, attachments: Dict[str, Any]) -> Dict[str, Any]:
        items = attachments.get("items", []) if isinstance(attachments, dict) else []
        mode = attachments.get("mode")
        preview_mode = "side-panel" if items else "inline"
        updated = {
            "mode": preview_mode,
            "items": items,
            "preview_variant": preview_mode,
            "non_blocking": True,
        }
        return updated

    def _differentiate_notes(self, notes: List[Dict[str, Any]]) -> List[str]:
        flags: List[str] = []
        visibilities = {note.get("visibility") for note in notes}
        for note in notes:
            if note.get("visibility") == "internal":
                note["style"] = "muted-panel"
                note["channel_label"] = "Internal note"
            else:
                note["style"] = "elevated-panel"
                note["channel_label"] = "Customer reply"
        if len(visibilities) > 1:
            flags.append("mis-operation-prevented")
        return flags

    def _enforce_confirmations(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        enhanced = []
        for action in actions:
            if not isinstance(action, dict):
                continue
            if action.get("critical"):
                action["requires_confirmation"] = True
                action["confirmation_copy"] = f"Confirm {action.get('label', action.get('id'))}"
            enhanced.append(action)
        return enhanced

    def _compute_metrics(self, layout: Dict[str, Any], flags: List[str]) -> Dict[str, Any]:
        sections = layout.get("sections", [])
        attachments = layout.get("attachments", {})
        notes = layout.get("notes", [])
        actions = layout.get("actions", [])

        collapsed_sections = sum(1 for sec in sections if sec.get("collapsed"))
        history_entries = sum(
            len(sec.get("items", []))
            for sec in sections
            if sec.get("category") in TIMELINE_CATEGORIES
        )
        clarity_score = self._clarity_score(sections, attachments, notes, actions, flags)
        scroll_savings = collapsed_sections * 12 + max(0, history_entries - 10)
        misoperation_risk = self._misoperation_risk(notes, actions)
        attachment_non_blocking = attachments.get("mode") != "fullscreen"
        edge_case_coverage = self._edge_case_coverage(flags, collapsed_sections, attachment_non_blocking)

        return {
            "clarity_score": clarity_score,
            "collapsed_sections": collapsed_sections,
            "scroll_savings": scroll_savings,
            "misoperation_risk": misoperation_risk,
            "attachment_non_blocking": attachment_non_blocking,
            "edge_case_coverage": edge_case_coverage,
        }

    def _clarity_score(
        self,
        sections: List[Dict[str, Any]],
        attachments: Dict[str, Any],
        notes: List[Dict[str, Any]],
        actions: List[Dict[str, Any]],
        flags: List[str],
    ) -> int:
        score = 55
        if sections and sections[0].get("category") == "core":
            score += 15
        if any(sec.get("collapsed") for sec in sections if sec.get("category") in TIMELINE_CATEGORIES):
            score += 10
        if attachments.get("mode") != "fullscreen":
            score += 5
        if self._notes_differentiated(notes):
            score += 10
        if self._has_confirmations(actions):
            score += 5
        if "html-neutralized" in flags:
            score += 5
        return min(score, 95)

    def _misoperation_risk(self, notes: List[Dict[str, Any]], actions: List[Dict[str, Any]]) -> int:
        risk = 30
        if self._notes_differentiated(notes):
            risk -= 15
        if self._has_confirmations(actions):
            risk -= 10
        return max(5, risk)

    def _edge_case_coverage(
        self, flags: List[str], collapsed_sections: int, attachment_non_blocking: bool
    ) -> int:
        score = 65 + collapsed_sections * 5
        if attachment_non_blocking:
            score += 5
        score += 5 * len(flags)
        return min(score, 95)

    def _add_flag(self, flags: List[str], flag: str) -> None:
        if flag not in flags:
            flags.append(flag)

    def _has_confirmations(self, actions: List[Dict[str, Any]]) -> bool:
        return any(action.get("requires_confirmation") for action in actions if isinstance(action, dict))

    def _notes_differentiated(self, notes: List[Dict[str, Any]]) -> bool:
        styles = {note.get("style") for note in notes if note.get("style")}
        return len(styles) >= 2

    def _flatten_sections(self, sections: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        flat: List[Dict[str, Any]] = []
        max_depth = 1

        def _walk(section: Dict[str, Any], depth: int = 1) -> None:
            nonlocal max_depth
            max_depth = max(max_depth, depth)
            cleaned = {
                "id": section.get("id"),
                "title": section.get("title"),
                "category": section.get("category"),
                "collapsed": bool(section.get("collapsed", False)),
                "items": section.get("items", []) or [],
                "children": [],
            }
            flat.append(cleaned)
            for child in section.get("children", []) or []:
                if isinstance(child, dict):
                    _walk(child, depth + 1)

        for section in sections:
            if isinstance(section, dict):
                _walk(section)
        return flat, max_depth

    def _is_core_section(self, section: Dict[str, Any]) -> bool:
        if section.get("category") == "core":
            return True
        for item in section.get("items", []):
            if not isinstance(item, dict):
                continue
            if item.get("field") in CORE_FIELDS:
                return True
        return False
