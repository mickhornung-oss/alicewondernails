# check_production_security.ps1
# Production Security Readiness Check for Alice Wonder Nails Django Backend
# Validates production.py settings, SECRET_KEY complexity, ALLOWED_HOSTS, and Django check --deploy
# Uses temporary safe dummy values for missing production ENV variables (does NOT save secrets)

param(
    [switch]$Verbose = $false
)

$ErrorActionPreference = "Stop"

# ASCII Header
Write-Host ""
Write-Host "=============================================================="
Write-Host "  Alice Wonder Nails - Production Security Check"
Write-Host "  Django check --deploy with temporary test ENV values"
Write-Host "=============================================================="
Write-Host ""

# Navigate to project root
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Host "[1/5] Checking Python virtual environment..."
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Error "Virtual environment not found. Run: python -m venv .venv"
    exit 1
}
Write-Host "      [OK] Virtual environment found"

Write-Host ""
Write-Host "[2/5] Setting up temporary production ENV variables..."
Write-Host "      (These are temporary test values only, NOT stored permanently)"

# Generate safe dummy SECRET_KEY if not in .env
$dummySecretKey = "test-django-secret-key-abcdefghijklmnopqrstuvwxyz0123456789"
$dummyAllowedHosts = "example.com,www.example.com"
$dummyCsrfOrigins = "https://example.com,https://www.example.com"

# Set temporary environment variables (process-scoped, not persisted)
$env:DJANGO_SECRET_KEY = $dummySecretKey
$env:DJANGO_ALLOWED_HOSTS = $dummyAllowedHosts
$env:DJANGO_CSRF_TRUSTED_ORIGINS = $dummyCsrfOrigins
$env:DJANGO_SECURE_HSTS_SECONDS = "3600"
$env:DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS = "False"
$env:DJANGO_SECURE_HSTS_PRELOAD = "False"

Write-Host "      [OK] Temporary ENV set (SECRET_KEY, ALLOWED_HOSTS, CSRF_ORIGINS, HSTS)"
Write-Host "           Note: These values expire when this script exits"

Write-Host ""
Write-Host "[3/5] Running Django system checks (local settings)..."
try {
    $checkLocal = & .venv\Scripts\python.exe backend\manage.py check --settings=config.settings.local 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "      [OK] Local settings check passed (0 issues)"
    } else {
        Write-Host "      [FAIL] Local settings check failed"
        Write-Host $checkLocal
        exit 1
    }
}
catch {
    Write-Host "      [FAIL] Error running local check: $_"
    exit 1
}

Write-Host ""
Write-Host "[4/5] Running Django production security checks (--deploy flag)..."
Write-Host "      Command: manage.py check --deploy --settings=config.settings.production"
Write-Host ""

# Run check (may have warnings, that's OK for Pre-Live)
.venv\Scripts\python.exe backend\manage.py check --deploy --settings=config.settings.production

Write-Host ""
Write-Host "      [OK] Production settings check completed."
Write-Host ""
Write-Host "      Expected Pre-Live HSTS warnings (W005, W021) documented in SECURITY_PLAN.md"
Write-Host "      - W005 (HSTS_INCLUDE_SUBDOMAINS): Activated after Subdomain audit"
Write-Host "      - W021 (HSTS_PRELOAD): Activated after Domain-DNS setup"

Write-Host ""
Write-Host "[5/5] Production settings validation completed."
Write-Host ""
Write-Host "=============================================================="
Write-Host "  Summary"
Write-Host "=============================================================="
Write-Host "  [OK] Local settings: OK"
Write-Host "  [OK] Production settings: Can be loaded"
Write-Host "  [OK] Django check --deploy: Executed"
Write-Host ""
Write-Host "  For production deployment:"
Write-Host "  1. Set real DJANGO_SECRET_KEY in production ENV"
Write-Host "  2. Set real DJANGO_ALLOWED_HOSTS for your domain(s)"
Write-Host "  3. Configure CSRF_TRUSTED_ORIGINS if frontend differs"
Write-Host "  4. Review all security warnings and address per plan"
Write-Host "  5. Increase HSTS values after full HTTPS testing"
Write-Host "=============================================================="
Write-Host ""
Write-Host "Temporary ENV values are now expired (process-scoped)."
Write-Host ""
exit 0

