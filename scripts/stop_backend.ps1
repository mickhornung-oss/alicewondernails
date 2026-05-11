param()

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error 'Python wurde nicht gefunden. Bitte prüfen Sie Ihre PATH-Variable.'
    exit 1
}

$processes = Get-CimInstance Win32_Process | Where-Object {
    ($_.CommandLine -and $_.CommandLine -match 'manage\.py.*runserver') -or
    ($_.CommandLine -and $_.CommandLine -match 'django\.core\.management\.execute_from_command_line')
}

if (-not $processes) {
    Write-Host 'Kein laufender Django-Backend-Prozess gefunden.' -ForegroundColor Yellow
    exit 0
}

foreach ($process in $processes) {
    Write-Host "Beende Prozess: $($process.ProcessId) - $($process.CommandLine)"
    Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
}

Write-Host 'Backend-Prozess(e) gestoppt.' -ForegroundColor Green
