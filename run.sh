#!/usr/bin/env bash
# Start IAM Desk on macOS/Linux. Creates a virtual environment on first run.
set -e
cd "$(dirname "$0")"
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt
python -m backend.app
