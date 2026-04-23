#!/bin/bash
set -e
VENV=${VENV:-/tmp/voice-obs-venv}
if [ ! -d "$VENV" ]; then
  uv venv "$VENV" --python python3
  uv pip install --python "$VENV/bin/python3" basilisp hy
fi
cd "$(dirname "$0")"
PYTHONPATH=. "$VENV/bin/basilisp" run observatory.lpy
