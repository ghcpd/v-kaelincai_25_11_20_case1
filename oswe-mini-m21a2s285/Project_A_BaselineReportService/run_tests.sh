#!/usr/bin/env bash
set -e
python -m pytest -q --disable-warnings --maxfail=1
