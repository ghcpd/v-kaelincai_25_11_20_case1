#!/bin/bash
set -e
python -m venv .env
. .env/bin/activate
pip install -r requirements.txt
