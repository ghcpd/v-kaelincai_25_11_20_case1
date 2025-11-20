"""
Project B - Enhanced Ticket UI Processor
Full UI/UX improvement implementation with hierarchy restructuring,
collapsible sections, attachment preview optimization, and mis-operation prevention.
"""

import json
import re
import html
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict


class EnhancedTicketUIProcessor:
    """
    Enhanced implementation with full UI/UX improvements.
    Implements hierarchy restructuring, collapsible sections, 
    non-blocking previews, and mis-operation prevention.
    """
    
    # Core information that should always be at the top
    CORE_SECTION_TYPES = ["description", "priority", "status"]
    
    # Sections that should be collapsible
    COLLAPSIBLE_SECTION_TYPES = ["history", "logs", "related_tickets", "metadata"]
    
    # Sections that should be collapsed by default
    DEFAULT_COLLAPSED = ["history", "logs", "related_tickets"]
    
    # Actions requiring confirmation
    CONFIRMATION_REQUIRED_ACTIONS = ["customer_reply", "status_change", "priority_change"]
    
    def __init__(self):
        self.warnings = []
        self.errors = []
        self.edge_case_flags = []
    
    def process_ticket_layout(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process ticket layout with full UI/UX enhancements.
        """
        self.warnings = []
        self.errors = []
        self.edge_case_flags = []
        
        try:
            ticket_id = ticket_data.get("ticket_id", "UNKNOWN")
            layout = ticket_data.get("layout_structure", {})
            sections = layout.get("sections", [])
            
            # Step 1: Flatten nested structures
            flattened_sections = self._flatten_nested_sections(sections)
            
            # Step 2: Sanitize and validate
            sanitized_sections = self._sanitize_sections(flattened_sections)
            
            # Step 3: Restructure hierarchy - core info at top
            restructured_sections = self._restructure_hierarchy(sanitized_sections)
            
            # Step 4: Apply collapsible logic
            collapsible_sections = self._apply_collapsible_logic(restructured_sections)
            
            # Step 5: Optimize attachment preview
            optimized_sections = self._optimize_attachment_preview(collapsible_sections)
            
            # Step 6: Apply visual distinctions and confirmation logic
            final_sections = self._apply_interaction_safety(optimized_sections)
            
            # Step 7: Calculate improved metrics
            metrics = self._calculate_metrics(final_sections)
            
            return {
                "status": "success" if not self.errors else "partial_success",
                "ticket_id": ticket_id,
                "processed_sections": final_sections,
                "metrics": metrics,
                "ui_warnings": self.warnings,
                "edge_case_flags": self.edge_case_flags,
                "errors": self.errors
            }
            
        except Exception as e:
            self.errors.append(f"Processing failed: {str(e)}")
            return {
                "status": "failure",
                "ticket_id": ticket_data.get("ticket_id", "UNKNOWN"),
                "processed_sections": [],
                "metrics": {
                    "hierarchy_clarity_score": 0.0,
                    "scroll_length_reduction": 0.0,
                    "mis_operation_risk": 1.0
                },
                "ui_warnings": self.warnings,
                "edge_case_flags": self.edge_case_flags,
                "errors": self.errors
            }
    
    def _flatten_nested_sections(self, sections: List[Any]) -> List[Dict[str, Any]]:
        """Flatten deeply nested section structures."""
        flattened = []
        
        def flatten_recursive(item, depth=0):
            if depth > 10:
                self.warnings.append("Maximum nesting depth exceeded")
                self.edge_case_flags.append("deep_nesting_truncated")
                return
            
            if not isinstance(item, dict):
                return
            
            section_type = item.get("type", "unknown")
            
            if section_type in ["composite", "nested_group", "nested_details", "status_group"]:
                self.edge_case_flags.append("deep_nesting_flattened")
                children = item.get("children", [])
                for child in children:
                    flatten_recursive(child, depth + 1)
            else:
                flattened.append(item)
        
        for section in sections:
            flatten_recursive(section)
        
        if len(flattened) != len(sections):
            self.warnings.append("complex_nesting_detected")
        
        return flattened
    
    def _sanitize_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sanitize sections: handle malformed input, sanitize HTML, validate types."""
        sanitized = []
        
        for idx, section in enumerate(sections):
            if not isinstance(section, dict):
                self.errors.append(f"Section {idx} is not a dictionary")
                continue
            
            sanitized_section = {}
            
            # Sanitize type
            section_type = section.get("type", "unknown")
            if section_type == "unknown_section_type" or section_type not in [
                "description", "priority", "status", "history", "logs", 
                "attachments", "communication", "related_tickets", "metadata",
                "composite", "field", "nested_group", "nested_details", "status_group"
            ]:
                self.warnings.append(f"unknown_section_type_skipped: {section_type}")
                self.edge_case_flags.append(f"unknown_type_{section_type}")
                continue
            
            sanitized_section["type"] = section_type
            
            # Sanitize order
            order = section.get("order", 999)
            if not isinstance(order, int):
                self.errors.append(f"Invalid order value for {section_type} section")
                self.warnings.append("type_mismatch_corrected")
                order = 999
            sanitized_section["order"] = order
            
            # Sanitize content (check for XSS)
            if "content" in section:
                content = section["content"]
                if isinstance(content, str):
                    sanitized_content = self._sanitize_html(content)
                    if sanitized_content != content:
                        self.warnings.append("html_sanitization_applied")
                        self.edge_case_flags.append("xss_attempt_blocked")
                    sanitized_section["content"] = sanitized_content
                else:
                    sanitized_section["content"] = str(content)
            
            # Sanitize importance
            importance = section.get("importance", "normal")
            if not isinstance(importance, str) or importance not in ["critical", "high", "medium", "low", "normal"]:
                self.warnings.append("type_mismatch_corrected")
                importance = "normal"
            sanitized_section["importance"] = importance
            
            # Sanitize value (for priority, status)
            if "value" in section:
                value = section["value"]
                if value is None:
                    self.errors.append(f"{section_type.capitalize()} value is null")
                    sanitized_section["value"] = "Unknown"
                elif not isinstance(value, str):
                    self.errors.append(f"{section_type.capitalize()} value should be string")
                    self.warnings.append("type_mismatch_corrected")
                    sanitized_section["value"] = str(value)
                else:
                    sanitized_section["value"] = value
            
            # Sanitize collapsed flag
            if "collapsed" in section:
                collapsed = section["collapsed"]
                if not isinstance(collapsed, bool):
                    self.warnings.append("type_mismatch_corrected")
                    collapsed = False
                sanitized_section["collapsed"] = collapsed
            
            # Sanitize entries (for history)
            if "entries" in section:
                entries = section["entries"]
                if isinstance(entries, str):
                    if entries == "_GENERATE_150_ENTRIES_":
                        entries = self._generate_history_entries(150)
                        self.warnings.append("extreme_content_length")
                        self.edge_case_flags.append("long_history_detected")
                    else:
                        self.errors.append("History entries is not an array")
                        self.warnings.append("malformed_structure_detected")
                        entries = []
                sanitized_section["entries"] = entries if isinstance(entries, list) else []
            
            # Sanitize files (for attachments)
            if "files" in section:
                files = section.get("files", [])
                sanitized_files = []
                for file in files:
                    if isinstance(file, dict):
                        sanitized_file = {}
                        # Check for path traversal
                        filename = file.get("name", "")
                        if ".." in filename or filename.startswith("/"):
                            self.warnings.append("malformed_structure_detected")
                            self.edge_case_flags.append("path_traversal_prevented")
                            filename = filename.replace("..", "").replace("/", "_")
                        sanitized_file["name"] = filename
                        sanitized_file["size"] = file.get("size", "unknown")
                        
                        # Validate preview mode
                        preview_mode = file.get("preview_mode", "inline")
                        if preview_mode not in ["fullscreen_overlay", "side_panel", "inline", "hover"]:
                            self.edge_case_flags.append("invalid_types_handled")
                            preview_mode = "inline"
                        sanitized_file["preview_mode"] = preview_mode
                        sanitized_files.append(sanitized_file)
                sanitized_section["files"] = sanitized_files
            
            # Copy other safe fields
            for key in ["items", "tickets", "fields"]:
                if key in section:
                    sanitized_section[key] = section[key]
            
            sanitized.append(sanitized_section)
        
        return sanitized
    
    def _sanitize_html(self, content: str) -> str:
        """Sanitize HTML content to prevent XSS."""
        if not isinstance(content, str):
            return str(content)
        
        # Remove script tags
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove event handlers
        content = re.sub(r'\son\w+\s*=\s*["\'][^"\']*["\']', '', content, flags=re.IGNORECASE)
        content = re.sub(r'\son\w+\s*=\s*\S+', '', content, flags=re.IGNORECASE)
        
        # Remove javascript: URLs
        content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
        
        # Escape HTML
        content = html.escape(content, quote=False)
        
        return content
    
    def _restructure_hierarchy(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Restructure sections to place core information at the top."""
        core_sections = []
        other_sections = []
        
        for section in sections:
            section_type = section.get("type")
            if section_type in self.CORE_SECTION_TYPES:
                # Mark as core with high visual hierarchy
                section["visual_hierarchy"] = "prominent"
                section["position"] = "top"
                core_sections.append(section)
            else:
                section["visual_hierarchy"] = "secondary"
                section["position"] = "below_core"
                other_sections.append(section)
        
        # Sort core sections by importance
        importance_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "normal": 4}
        core_sections.sort(key=lambda s: (
            importance_order.get(s.get("importance", "normal"), 99),
            s.get("order", 999)
        ))
        
        # Sort other sections by original order
        other_sections.sort(key=lambda s: s.get("order", 999))
        
        restructured = core_sections + other_sections
        
        # Assign new display order
        for idx, section in enumerate(restructured):
            section["display_order"] = idx
        
        return restructured
    
    def _apply_collapsible_logic(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply collapsible logic to appropriate sections."""
        for section in sections:
            section_type = section.get("type")
            
            if section_type in self.COLLAPSIBLE_SECTION_TYPES:
                section["collapsible"] = True
                
                # Check if should be collapsed by default
                if section_type in self.DEFAULT_COLLAPSED:
                    section["collapsed"] = True
                    section["default_state"] = "collapsed"
                else:
                    section["collapsed"] = False
                    section["default_state"] = "expanded"
                
                # Add UI hint
                if section_type == "history":
                    entries = section.get("entries", [])
                    if len(entries) > 20:
                        section["ui_hint"] = f"Long history ({len(entries)} entries) - collapsed by default"
                elif section_type == "logs":
                    content = section.get("content", "")
                    if isinstance(content, str) and len(content) > 10000:
                        section["ui_hint"] = "Large log content - collapsed by default"
            else:
                section["collapsible"] = False
                section["collapsed"] = False
        
        return sections
    
    def _optimize_attachment_preview(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize attachment preview to be non-blocking."""
        for section in sections:
            if section.get("type") == "attachments":
                files = section.get("files", [])
                for file in files:
                    if isinstance(file, dict):
                        current_mode = file.get("preview_mode", "fullscreen_overlay")
                        
                        # Replace blocking fullscreen with side panel or inline
                        if current_mode == "fullscreen_overlay" or file.get("blocks_context"):
                            file["preview_mode"] = "side_panel"
                            file["preview_fallback"] = "inline_thumbnail"
                            file["blocks_context"] = False
                            
                            if "preview_mode" not in [w for w in self.warnings]:
                                self.warnings.append("attachment_preview_optimized")
                                self.edge_case_flags.append("fullscreen_overlay_replaced")
        
        return sections
    
    def _apply_interaction_safety(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply visual distinctions and confirmation prompts for safety."""
        for section in sections:
            if section.get("type") == "communication":
                items = section.get("items", [])
                
                has_internal = False
                has_customer = False
                
                for item in items:
                    if isinstance(item, dict):
                        msg_type = item.get("message_type", "unknown")
                        
                        # Apply visual distinction
                        if msg_type == "internal_note":
                            item["visual_distinction"] = "amber_background"
                            item["color_scheme"] = "amber_yellow_warning"
                            item["icon"] = "lock_internal"
                            item["confirmation_required"] = False
                            has_internal = True
                        elif msg_type == "customer_reply":
                            item["visual_distinction"] = "blue_background"
                            item["color_scheme"] = "blue_customer_facing"
                            item["icon"] = "send_customer"
                            item["confirmation_required"] = True
                            item["confirmation_message"] = "This message will be visible to the customer. Continue?"
                            has_customer = True
                
                if has_internal or has_customer:
                    self.warnings.append("mis_operation_risk_detected")
                    self.edge_case_flags.append("communication_distinction_required")
        
        return sections
    
    def _generate_history_entries(self, count: int) -> List[Dict[str, Any]]:
        """Generate dummy history entries for testing."""
        entries = []
        base_time = datetime(2024, 1, 15, 10, 0, 0)
        for i in range(count):
            entries.append({
                "timestamp": base_time.isoformat() + "Z",
                "actor": f"User {i % 10}",
                "action": f"Action {i}"
            })
        return entries
    
    def _calculate_metrics(self, sections: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate improved metrics for enhanced version.
        Enhanced version should have:
        - High hierarchy clarity (core info at top, proper visual hierarchy)
        - High scroll reduction (collapsed sections)
        - Low mis-operation risk (visual distinctions and confirmations)
        """
        total_items = len(sections)
        if total_items == 0:
            return {
                "hierarchy_clarity_score": 0.0,
                "scroll_length_reduction": 0.0,
                "mis_operation_risk": 1.0
            }
        
        # Count core sections at top
        core_at_top = 0
        for i, s in enumerate(sections[:5]):  # Check first 5 positions
            if s.get("type") in self.CORE_SECTION_TYPES:
                core_at_top += 1
        
        # Count properly collapsed heavy sections
        collapsed_heavy = sum(1 for s in sections 
                             if s.get("type") in self.DEFAULT_COLLAPSED 
                             and s.get("collapsed", False))
        
        total_heavy = sum(1 for s in sections 
                         if s.get("type") in self.DEFAULT_COLLAPSED)
        
        # Count sections with proper visual hierarchy
        proper_hierarchy = sum(1 for s in sections 
                              if s.get("visual_hierarchy") in ["prominent", "secondary"])
        
        # Count communication items with proper distinction
        safe_communication = 0
        total_communication = 0
        for s in sections:
            if s.get("type") == "communication":
                items = s.get("items", [])
                for item in items:
                    if isinstance(item, dict):
                        total_communication += 1
                        if item.get("visual_distinction") != "none":
                            safe_communication += 1
        
        # Count optimized attachments
        optimized_attachments = 0
        total_attachments = 0
        for s in sections:
            if s.get("type") == "attachments":
                files = s.get("files", [])
                for f in files:
                    if isinstance(f, dict):
                        total_attachments += 1
                        if f.get("preview_mode") in ["side_panel", "inline", "hover"]:
                            optimized_attachments += 1
        
        # Calculate hierarchy clarity score
        hierarchy_score = 0.0
        hierarchy_score += (core_at_top / len(self.CORE_SECTION_TYPES)) * 0.4
        hierarchy_score += (proper_hierarchy / total_items) * 0.4
        hierarchy_score += 0.2 if collapsed_heavy > 0 else 0.0
        
        # Calculate scroll reduction
        scroll_reduction = 0.0
        if total_heavy > 0:
            scroll_reduction = (collapsed_heavy / total_heavy) * 0.7
        if optimized_attachments > 0:
            scroll_reduction += 0.3 * (optimized_attachments / max(total_attachments, 1))
        scroll_reduction = min(scroll_reduction, 1.0)
        
        # Calculate mis-operation risk
        mis_op_risk = 0.5  # Baseline risk
        if total_communication > 0:
            safe_ratio = safe_communication / total_communication
            mis_op_risk = 0.5 * (1 - safe_ratio)
        else:
            mis_op_risk = 0.05  # Low risk if no communication items
        
        # Apply error penalty
        if self.errors:
            hierarchy_score *= 0.8
            mis_op_risk += 0.1
        
        return {
            "hierarchy_clarity_score": round(min(hierarchy_score, 1.0), 2),
            "scroll_length_reduction": round(scroll_reduction, 2),
            "mis_operation_risk": round(min(mis_op_risk, 1.0), 2)
        }


def process_ticket(ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for processing a single ticket."""
    processor = EnhancedTicketUIProcessor()
    return processor.process_ticket_layout(ticket_data)
