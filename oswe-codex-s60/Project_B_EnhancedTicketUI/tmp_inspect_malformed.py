import json
from src.transformer import transform
from pathlib import Path
scenarios = json.loads((Path(__file__).resolve().parents[1] / 'test_scenarios.json').read_text())
mal = [sc for sc in scenarios if sc['id']=='malformed_input_with_unsafe_html'][0]
res = transform(mal['initial_layout'], scenario_id=mal['id'])
print(json.dumps(res, indent=2))
