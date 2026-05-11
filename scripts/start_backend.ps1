param()

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$backendPath = Join-Path $projectRoot '..\backend' | Resolve-Path -ErrorAction SilentlyContinue
if (-not $backendPath) {
    Write-Error 'backend-Verzeichnis wurde nicht gefunden. Stellen Sie sicher, dass dieses Skript im scripts-Ordner ausgeführt wird.'
    exit 1
}

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

$managePath = Join-Path $backendPath 'manage.py'
if (-not (Test-Path $managePath)) {
    Write-Error 'manage.py nicht gefunden. Das Backend ist nicht korrekt eingerichtet.'
    exit 1
}

$requirementsPath = Join-Path $backendPath 'requirements.txt'
if (-not (Test-Path $requirementsPath)) {
    Write-Warning 'requirements.txt nicht gefunden. Es kann sein, dass Abhängigkeiten fehlen.'
} else {
    try {
        & $python -m pip show django > $null 2>&1
    } catch {
        Write-Warning 'Django scheint nicht installiert zu sein. Bitte installieren Sie die Abhängigkeiten manuell mit .venv\Scripts\python.exe -m pip install -r backend\requirements.txt.'
    }
}

$envFile = Join-Path (Split-Path $backendPath -Parent) '.env'
if (-not (Test-Path $envFile)) {
    Write-Warning '.env nicht gefunden. Kopieren Sie backend\.env.example nach .env und passen Sie die Werte an.'
}

Write-Host 'Starte Django Development Server...' -ForegroundColor Green
Set-Location $backendPath
& $python $managePath runserver 127.0.0.1:8000
