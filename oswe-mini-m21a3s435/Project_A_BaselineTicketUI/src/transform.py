from typing import Dict, Any


def baseline_transform(layout: Dict[str, Any]) -> Dict[str, Any]:
    """Baseline transformer: returns input mostly unchanged with minimal meta.

    Does not restructure layout, does not add collapsible sections, nor preview optimization.
    """
    out = {"status": "ok", "transformed": layout, "notes": ["baseline_pass"]}
    return out
