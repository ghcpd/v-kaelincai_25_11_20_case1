import json
import sys
from pathlib import Path
import pytest


@pytest.fixture(scope="session")
def scenarios():
    root = Path(__file__).resolve().parents[2]
    data = json.loads((root / "test_scenarios.json").read_text(encoding="utf-8"))
    return data


# Adjust sys.path for module imports
project_root = Path(__file__).resolve().parents[1]
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
