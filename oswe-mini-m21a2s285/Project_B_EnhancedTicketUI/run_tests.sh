#!/usr/bin/env bash
set -e
python -m pytest -q --disable-warnings --maxfail=1
python - <<'PY'
from src.transform import enhance_transform
import json
s = {'sections':[{'id':'summary','fields':[{'name':'problem_description','value':'p'},{'name':'priority','value':'high'}]}, {'id':'history','fields':[{'name':'h1'},{'name':'h2'}]}]}
print(json.dumps(enhance_transform(s), indent=2))
PY
