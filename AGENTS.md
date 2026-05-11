# Alice Wonder Nails - Agent Guidance

This repository now contains only the new V2 shop/platform foundation.

## What this repo is

- `backend/` contains the Django V2 backend foundation.
- `docs/` contains V2 project documentation.
- `docs/modules/` contains V2 module documentation.
- `scripts/` contains local V2 PowerShell scripts.
- There is no active frontend folder right now. It will be created later in a dedicated frontend block.

The old static V1 website, STRATO upload package, FastAPI/SQLite backend, archive folders, runtime data and legacy assets have been removed from this project folder because the user has an external backup.

## Key conventions for agents

- Work only inside `C:\Users\mickh\Desktop\alice-wondernails`.
- Do not create new archive, legacy, old, backup or STRATO folders in this project.
- Do not add or commit secrets, `.env`, runtime data, logs, SQLite databases, CSV exports or generated local state.
- Keep `.env` and `.venv/` local and ignored.
- Backend runtime configuration comes from `.env` and `backend/config/settings/`.
- PostgreSQL setup is green after Arbeitsblock 02. `scripts\check_postgres.ps1`, migrations and backend pytest passed.

## Local development commands

- Start backend: `powershell -ExecutionPolicy Bypass -File .\scripts\start_backend.ps1`
- Stop backend: `powershell -ExecutionPolicy Bypass -File .\scripts\stop_backend.ps1`
- Backend status: `powershell -ExecutionPolicy Bypass -File .\scripts\status_backend.ps1`
- Run backend tests: `powershell -ExecutionPolicy Bypass -File .\scripts\test_backend.ps1`
- Set up PostgreSQL: `powershell -ExecutionPolicy Bypass -File .\scripts\setup_postgres_local.ps1`
- Check PostgreSQL: `powershell -ExecutionPolicy Bypass -File .\scripts\check_postgres.ps1`

## Important files and directories

- `backend/manage.py` - Django management entry point
- `backend/config/settings/base.py` - shared Django settings
- `backend/config/settings/local.py` - local settings
- `backend/apps/core/` - first V2 core app and healthcheck
- `backend/.env.example` - backend environment template with placeholders
- `docs/PROJECT_MASTER.md` - project master truth
- `docs/PROGRESS.md` - running work log
- `docs/CLEANUP_PLAN.md` - cleanup policy and status
- `docs/BACKEND_BLUEPRINT.md` - backend architecture notes
- `docs/INFRASTRUCTURE_STATUS.md` - PostgreSQL, logging, email status

## Current block boundary

Accounts/Roles/Profiles foundation exists after Arbeitsblock 02. Do not start products, catalog, pricing, cart, checkout, payment, shipping or frontend UI until the next explicit block.
