# BUILD-LOG

Reverse-chronological log of what got built, by an autonomous session.

## 2026-06-25 — Session 1 (autonomous)

### Environment
- Working dir was empty. Spec `.md` files not on disk → built from the prompt summary.
- Toolchain found: **Python 3.8.10**, **git 2.54**. **No Node/npm.**
- Installed + verified **FastAPI 0.124 + uvicorn** → backend is runnable now.
- Decision: ship a zero-install `preview.html` (CDN React+Tailwind) for immediate
  click-around since Vite can't run here; real Vite app lives in `frontend/`.

### Scaffold
- `git init`; `.gitignore`, `.env.example`, `README.md`, `run.ps1`, `run.sh`.
- `NEEDS-FROM-YOU.md` with 5 stubbed items + plug-in points.

<!-- newest entries go ABOVE this line as work proceeds -->
