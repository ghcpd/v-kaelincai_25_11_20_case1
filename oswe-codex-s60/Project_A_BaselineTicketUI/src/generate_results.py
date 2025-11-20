import json
from pathlib import Path
from datetime import datetime
from .transformer import transform


def main():
    project_root = Path(__file__).resolve().parents[1]
    scenarios_path = project_root.parents[0] / "test_scenarios.json"
    results_dir = project_root / "results"
    logs_dir = project_root / "logs"
    results_dir.mkdir(exist_ok=True)
    logs_dir.mkdir(exist_ok=True)

    scenarios = json.loads(scenarios_path.read_text(encoding="utf-8"))
    outputs = []
    log_lines = []
    for sc in scenarios:
        sid = sc.get("id")
        layout = sc.get("initial_layout")
        result = transform(layout, scenario_id=sid)
        outputs.append(result)
        log_lines.append(f"[{sid}] status={result.get('status')} metrics={result.get('metrics')}")

    (results_dir / "results_pre.json").write_text(json.dumps(outputs, indent=2), encoding="utf-8")
    timestamp = datetime.utcnow().isoformat()
    (logs_dir / "log_pre.txt").write_text("\n".join([timestamp] + log_lines), encoding="utf-8")
    print(f"Wrote results_pre.json with {len(outputs)} scenarios")


if __name__ == "__main__":
    main()
