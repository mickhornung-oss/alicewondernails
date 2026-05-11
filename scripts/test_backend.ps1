param()

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvPython = Join-Path $projectRoot '..\.venv\Scripts\python.exe' | Resolve-Path -ErrorAction SilentlyContinue
if ($venvPython) {
    $python = $venvPython
} else {
    $python = Get-Command python -ErrorAction SilentlyContinue
}

if (-not $python) {
    Write-Error 'Python wurde nicht gefunden. Bitte installieren Sie Python oder passen Sie den PATH an.'
    exit 1
}

$backendPath = Join-Path $projectRoot '..\backend' | Resolve-Path -ErrorAction SilentlyContinue
if (-not $backendPath) {
    Write-Error 'backend-Verzeichnis wurde nicht gefunden.'
    exit 1
}

$requirementsPath = Join-Path $backendPath 'requirements.txt'
if (-not (Test-Path $requirementsPath)) {
    Write-Warning 'requirements.txt nicht gefunden. Tests könnten fehlschlagen.'
}

Set-Location $backendPath
Write-Host 'Führe pytest im Backend aus...' -ForegroundColor Green
& $python -m pytest
exit $LASTEXITCODE
