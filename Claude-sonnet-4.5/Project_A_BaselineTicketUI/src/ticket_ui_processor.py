"""
Project A - Baseline Ticket UI Processor
Simple monolithic transformation with no hierarchy restructuring,
no collapsible sections, no preview optimization, and no mis-operation prevention.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class BaselineTicketUIProcessor:
    """
    Baseline implementation that processes ticket layouts without any optimization.
    This represents the "before" state with all the problems.
    """
    
    def __init__(self):
        self.warnings = []
        self.errors = []
        self.edge_case_flags = []
    
    def process_ticket_layout(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process ticket layout with minimal transformation.
        No hierarchy restructuring, everything stays in original order.
        """
        self.warnings = []
        self.errors = []
        self.edge_case_flags = []
        
        try:
            ticket_id = ticket_data.get("ticket_id", "UNKNOWN")
            layout = ticket_data.get("layout_structure", {})
            sections = layout.get("sections", [])
            
            # Baseline: Just pass through sections as-is with minimal processing
            processed_sections = []
            for section in sections:
                processed_section = self._process_section(section)
                if processed_section:
                    processed_sections.append(processed_section)
            
            # Calculate basic metrics (will be poor for baseline)
            metrics = self._calculate_metrics(processed_sections)
            
            return {
                "status": "success" if not self.errors else "failure",
                "ticket_id": ticket_id,
                "processed_sections": processed_sections,
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
    
    def _process_section(self, section: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual section - baseline does minimal work."""
        if not isinstance(section, dict):
            self.errors.append(f"Section is not a dictionary: {type(section)}")
            return None
        
        section_type = section.get("type", "unknown")
        
        # Baseline: Keep everything in original order, no collapsing
        processed = {
            "type": section_type,
            "order": section.get("order", 999),
            "collapsed": False,  # Baseline never collapses anything
            "visual_hierarchy": "flat",  # No hierarchy
            "preview_mode": section.get("preview_mode", "default")
        }
        
        # Handle different section types minimally
        if section_type == "description":
            processed["content"] = section.get("content", "")
            processed["importance"] = "normal"  # Baseline ignores importance
            
        elif section_type == "priority":
            processed["value"] = section.get("value", "Unknown")
            processed["importance"] = "normal"
            
        elif section_type == "status":
            processed["value"] = section.get("value", "Unknown")
            processed["importance"] = "normal"
            
        elif section_type == "history":
            entries = section.get("entries", [])
            if isinstance(entries, str) and entries == "_GENERATE_150_ENTRIES_":
                entries = self._generate_history_entries(150)
            processed["entries"] = entries if isinstance(entries, list) else []
            processed["collapsed"] = False  # Never collapse
            
        elif section_type == "logs":
            processed["content"] = section.get("content", "")
            processed["collapsed"] = False  # Never collapse
            
        elif section_type == "attachments":
            files = section.get("files", [])
            processed["files"] = files
            # Baseline: Keep fullscreen overlay mode (blocking)
            for f in processed.get("files", []):
                if isinstance(f, dict):
                    f["preview_mode"] = "fullscreen_overlay"
                    
        elif section_type == "communication":
            items = section.get("items", [])
            processed["items"] = items
            # Baseline: No visual distinction between internal/customer
            for item in processed.get("items", []):
                if isinstance(item, dict):
                    item["visual_distinction"] = "none"
                    item["confirmation_required"] = False
                    
        elif section_type == "related_tickets":
            processed["tickets"] = section.get("tickets", [])
            processed["collapsed"] = False  # Never collapse
            
        elif section_type == "metadata":
            processed["fields"] = section.get("fields", [])
            
        elif section_type == "composite":
            # Baseline: Don't handle nesting well, just flatten naively
            children = section.get("children", [])
            processed["children"] = children
            
        else:
            # Unknown section type - baseline just passes it through
            processed["raw_data"] = section
        
        return processed
    
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
        Calculate metrics for baseline (will be poor).
        Baseline has:
        - Low hierarchy clarity (everything is flat)
        - No scroll reduction (nothing is collapsed)
        - High mis-operation risk (no distinctions or confirmations)
        """
        # Baseline metrics are poor
        total_items = len(sections)
        
        # Count uncollapsed heavy sections
        uncollapsed_heavy = sum(1 for s in sections 
                               if s.get("type") in ["history", "logs", "related_tickets"] 
                               and not s.get("collapsed", False))
        
        # Count sections without proper importance
        no_importance = sum(1 for s in sections 
                           if s.get("importance") == "normal" and 
                           s.get("type") in ["description", "priority", "status"])
        
        # Count communication items without distinction
        mis_op_risk_items = 0
        for s in sections:
            if s.get("type") == "communication":
                items = s.get("items", [])
                mis_op_risk_items += sum(1 for item in items 
                                        if isinstance(item, dict) and 
                                        item.get("visual_distinction") == "none")
        
        # Baseline scores are intentionally poor
        hierarchy_clarity_score = max(0.1, 0.4 - (no_importance * 0.1))
        scroll_length_reduction = 0.0  # No reduction at all
        mis_operation_risk = min(0.9, 0.3 + (mis_op_risk_items * 0.1))
        
        return {
            "hierarchy_clarity_score": round(hierarchy_clarity_score, 2),
            "scroll_length_reduction": round(scroll_length_reduction, 2),
            "mis_operation_risk": round(mis_operation_risk, 2)
        }


def process_ticket(ticket_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for processing a single ticket."""
    processor = BaselineTicketUIProcessor()
    return processor.process_ticket_layout(ticket_data)
