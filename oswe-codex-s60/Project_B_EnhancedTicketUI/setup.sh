#!/usr/bin/env bash
set -euo pipefail

VENV=".venv"
if [ ! -d "$VENV" ]; then
  python -m venv "$VENV"
fi

if [ "$OS" == "Windows_NT" ]; then
  # shellcheck disable=SC1091
  source "$VENV/Scripts/activate"
else
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
fi

pip install --upgrade pip
pip install -r requirements.txt

echo "Virtual environment ready."
