#!/usr/bin/env bash
# Wise Old Man OS — one-shot runner (macOS / Linux / Git-Bash)
# Boots FastAPI, which also serves the zero-install preview UI.
set -euo pipefail
cd "$(dirname "$0")/backend"

python -m pip install --quiet --disable-pip-version-check -r requirements.txt

echo ""
echo "  Wise Old Man OS — backend + preview"
echo "  UI:   http://127.0.0.1:8787/"
echo "  API:  http://127.0.0.1:8787/api/health"
echo "  Docs: http://127.0.0.1:8787/docs"
echo ""

exec python -m uvicorn app.main:app --host 127.0.0.1 --port 8787 --reload
