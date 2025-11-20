#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

bash "$ROOT_DIR/setup.sh"

if [ "$OS" == "Windows_NT" ]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/Scripts/activate"
else
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

pytest -q --disable-warnings --maxfail=1
python -m src.generate_results

echo "Enhanced tests and results generation completed."
