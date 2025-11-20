"""
Baseline ticket layout transformer that intentionally keeps the overloaded
structure so tests can validate the before-state of the UI/UX experience.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Tuple

CORE_FIELDS = {"problem_description", "priority", "status"}
TIMELINE_CATEGORIES = {"history", "logs", "related"}


class TicketLayoutTransformer:
    """Baseline implementation that mostly passes layouts through."""

    def transform(self, layout_def: Any) -> Dict[str, Any]:
        layout_copy = deepcopy(layout_def) if isinstance(layout_def, dict) else {}
        normalized, warnings, errors, flags, depth = self._normalize(layout_copy)
        metrics = self._compute_metrics(normalized, warnings, errors, depth)
        status = "degraded" if errors else "success"
        return {
            "status": status,
            "metrics": metrics,
            "ui_warnings": warnings,
            "edge_case_flags": flags,
            "errors": errors,
            "layout": normalized,
        }

    def _normalize(
        self, layout: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[str], List[str], List[str], int]:
        warnings: List[str] = []
        errors: List[str] = []
        flags: List[str] = []

        sections = layout.get("sections", [])
        if not isinstance(sections, list):
            errors.append("sections-not-list")
            warnings.append("invalid-layout")
            sections = []
        normalized_sections, max_depth = self._normalize_sections(sections)
        if max_depth > 2:
            warnings.append("deeply-nested")
            flags.append("nesting-ignored")

        notes = layout.get("notes", [])
        if not isinstance(notes, list):
            errors.append("notes-missing")
            notes = []

        attachments = layout.get("attachments", {})
        if not isinstance(attachments, dict):
            attachments = {}
        if attachments.get("mode") == "fullscreen":
            warnings.append("attachment-blocking")
        if attachments.get("unsafe_payload"):
            flags.append("unsafe-html-passed")

        actions = layout.get("actions", [])
        if not isinstance(actions, list):
            errors.append("actions-invalid")
            actions = []

        normalized = {
            "sections": normalized_sections,
            "notes": notes,
            "attachments": attachments or {"mode": "fullscreen", "items": []},
            "actions": actions,
            "meta": layout.get("meta", {}),
        }

        warnings.extend(self._derive_behavioral_warnings(normalized))
        return normalized, warnings, errors, flags, max_depth

    def _normalize_sections(self, sections: List[Any]) -> Tuple[List[Dict[str, Any]], int]:
        normalized: List[Dict[str, Any]] = []
        max_depth = 1
        for raw in sections:
            if not isinstance(raw, dict):
                continue
            section = {
                "id": raw.get("id"),
                "title": raw.get("title"),
                "category": raw.get("category"),
                "collapsed": bool(raw.get("collapsed", False)),
                "items": raw.get("items", []) or [],
                "children": raw.get("children", []) or [],
            }
            normalized.append(section)
            depth = self._max_depth(section)
            max_depth = max(max_depth, depth)
        return normalized, max_depth

    def _derive_behavioral_warnings(self, layout: Dict[str, Any]) -> List[str]:
        warnings: List[str] = []
        sections = layout.get("sections", [])
        if sections:
            core_index = next(
                (idx for idx, sec in enumerate(sections) if self._is_core_section(sec)), None
            )
            if core_index is not None and core_index != 0:
                warnings.append("core-info-not-first")
            for section in sections:
                if section.get("category") in TIMELINE_CATEGORIES and not section.get(
                    "collapsed", False
                ):
                    warnings.append("timeline-not-collapsed")
                    break
        notes = layout.get("notes", [])
        if self._notes_indistinguishable(notes):
            warnings.append("notes-indistinguishable")
        actions = layout.get("actions", [])
        if self._missing_confirmation(actions):
            warnings.append("missing-confirmation")
        return warnings

    def _compute_metrics(
        self,
        layout: Dict[str, Any],
        warnings: List[str],
        errors: List[str],
        depth: int,
    ) -> Dict[str, Any]:
        sections = layout.get("sections", [])
        attachments = layout.get("attachments", {})
        notes = layout.get("notes", [])
        actions = layout.get("actions", [])

        clarity_score = self._clarity_score(sections, attachments, notes, actions, depth)
        collapsed_sections = sum(1 for sec in sections if sec.get("collapsed"))
        history_items = self._count_history_entries(sections)
        scroll_savings = collapsed_sections * min(10, history_items // 5)
        misoperation_risk = self._misoperation_risk(notes, actions, attachments, errors)
        attachment_non_blocking = attachments.get("mode") != "fullscreen"
        edge_case_coverage = self._edge_case_coverage(warnings, errors, attachment_non_blocking)

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
        depth: int,
    ) -> int:
        if not sections:
            return 10
        score = 25
        if self._has_core_section(sections):
            score += 5
        if sections and self._is_core_section(sections[0]):
            score += 10
        if attachments.get("mode") != "fullscreen":
            score += 5
        if self._notes_indistinguishable(notes):
            score -= 5
        if self._missing_confirmation(actions):
            score -= 5
        if depth > 2:
            score -= 5
        return max(10, min(score, 60))

    def _misoperation_risk(
        self,
        notes: List[Dict[str, Any]],
        actions: List[Dict[str, Any]],
        attachments: Dict[str, Any],
        errors: List[str],
    ) -> int:
        risk = 40
        if self._notes_indistinguishable(notes):
            risk += 35
        if self._missing_confirmation(actions):
            risk += 15
        if attachments.get("mode") == "fullscreen":
            risk += 5
        if errors:
            risk += 5
        return max(15, min(risk, 95))

    def _edge_case_coverage(
        self, warnings: List[str], errors: List[str], attachment_non_blocking: bool
    ) -> int:
        base = 50
        base -= len(warnings) * 5
        base -= len(errors) * 7
        if not attachment_non_blocking:
            base -= 5
        return max(10, min(base, 40))

    def _notes_indistinguishable(self, notes: List[Dict[str, Any]]) -> bool:
        visibilities = {note.get("visibility") for note in notes}
        styles = {note.get("style") for note in notes if note.get("style")}
        if len(visibilities) <= 1:
            return True
        return len(styles) <= 1

    def _missing_confirmation(self, actions: List[Dict[str, Any]]) -> bool:
        for action in actions:
            if action and action.get("critical") and not action.get("requires_confirmation"):
                return True
        return False

    def _has_core_section(self, sections: List[Dict[str, Any]]) -> bool:
        return any(self._is_core_section(section) for section in sections)

    def _is_core_section(self, section: Dict[str, Any]) -> bool:
        if section.get("category") == "core":
            return True
        for item in section.get("items", []):
            if not isinstance(item, dict):
                continue
            field_name = item.get("field")
            if field_name in CORE_FIELDS:
                return True
        return False

    def _max_depth(self, section: Dict[str, Any], depth: int = 1) -> int:
        children = section.get("children") or []
        if not children:
            return depth
        return max(self._max_depth(child, depth + 1) for child in children if isinstance(child, dict))

    def _count_history_entries(self, sections: List[Dict[str, Any]]) -> int:
        total = 0
        for section in sections:
            if section.get("category") in TIMELINE_CATEGORIES:
                total += len(section.get("items", []))
        return total
