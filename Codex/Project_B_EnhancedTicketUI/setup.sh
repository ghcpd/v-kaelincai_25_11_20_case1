#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"

if command -v python3 >/dev/null 2>&1; then
  PY_CMD=("python3")
elif command -v python >/dev/null 2>&1; then
  PY_CMD=("python")
else
  WIN_PY_PATH=$(powershell.exe -NoProfile -Command "(Get-Command python).Source" 2>/dev/null | tr -d '\r')
  if [ -n "$WIN_PY_PATH" ]; then
    if command -v wslpath >/dev/null 2>&1; then
      POSIX_PATH=$(wslpath "$WIN_PY_PATH")
    else
      POSIX_PATH="$WIN_PY_PATH"
    fi
    PY_CMD=("$POSIX_PATH")
  else
    echo "Python interpreter not found."
    exit 1
  fi
fi

echo "Bootstrapping virtualenv via ${PY_CMD[*]}"

if [ ! -d "$VENV_DIR" ] || { [ ! -f "$VENV_DIR/Scripts/python.exe" ] && [ ! -f "$VENV_DIR/bin/python" ]; }; then
  rm -rf "$VENV_DIR"
  "${PY_CMD[@]}" -m venv --without-pip "$VENV_DIR"
fi
if [ -d "$VENV_DIR/Scripts" ]; then
  PYTHON_BIN="$VENV_DIR/Scripts/python"
else
  PYTHON_BIN="$VENV_DIR/bin/python"
fi

if ! "$PYTHON_BIN" -m pip --version >/dev/null 2>&1; then
  GET_PIP="$VENV_DIR/get-pip.py"
  curl -sS https://bootstrap.pypa.io/get-pip.py -o "$GET_PIP"
  "$PYTHON_BIN" "$GET_PIP"
fi
"$PYTHON_BIN" -m pip install --upgrade pip >/dev/null
"$PYTHON_BIN" -m pip install -r "$PROJECT_ROOT/requirements.txt"
