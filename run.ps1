# Wise Old Man OS — one-shot runner (Windows / PowerShell)
# Boots the FastAPI backend, which ALSO serves the zero-install preview UI.
# Then open http://127.0.0.1:8787/  ->  click around on mock data.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $root "backend")

# Install deps on first run (idempotent, quiet).
python -m pip install --quiet --disable-pip-version-check -r requirements.txt

Write-Host ""
Write-Host "  Wise Old Man OS — backend + preview" -ForegroundColor Green
Write-Host "  UI:   http://127.0.0.1:8787/" -ForegroundColor Cyan
Write-Host "  API:  http://127.0.0.1:8787/api/health" -ForegroundColor Cyan
Write-Host "  Docs: http://127.0.0.1:8787/docs" -ForegroundColor Cyan
Write-Host ""

python -m uvicorn app.main:app --host 127.0.0.1 --port 8787 --reload
