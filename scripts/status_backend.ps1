param()

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$venvPython = Join-Path $projectRoot '..\.venv\Scripts\python.exe' | Resolve-Path -ErrorAction SilentlyContinue
if (-not $venvPython) {
    Write-Warning '.venv nicht gefunden. Statusprüfung erfolgt mit PATH-Python.'
}

$backendPath = Resolve-Path (Join-Path $PSScriptRoot '..\backend') -ErrorAction SilentlyContinue
if (-not $backendPath) {
    Write-Error 'backend-Verzeichnis wurde nicht gefunden.'
    exit 1
}

Write-Host "Backend-Pfad: $backendPath"

$processes = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -and $_.CommandLine -match 'manage\.py.*runserver'
}

if ($processes) {
    Write-Host 'Backend läuft aktuell:' -ForegroundColor Green
    $processes | ForEach-Object {
        Write-Host "- PID: $($_.ProcessId), CommandLine: $($_.CommandLine)"
    }
} else {
    Write-Host 'Kein laufender Django-Backend-Prozess gefunden.' -ForegroundColor Yellow
}

$envFile = Join-Path (Split-Path $backendPath -Parent) '.env'
if (-not (Test-Path $envFile)) {
    Write-Warning '.env wurde nicht gefunden. Das lokale Backend könnte nicht vollständig konfiguriert sein.'
}
