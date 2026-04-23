#!/bin/bash
set -e
VENV=${VENV:-/tmp/voice-obs-venv}
if [ ! -d "$VENV" ]; then
  echo "bootstrapping venv at $VENV"
  uv venv "$VENV" --python python3
  uv pip install --python "$VENV/bin/python3" basilisp hy
fi
cd "$(dirname "$0")"
"$VENV/bin/python3" -c "import hy"
"$VENV/bin/basilisp" run observatory.lpy
